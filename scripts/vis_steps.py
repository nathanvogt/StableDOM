from generate_vis import visualize
from absl import app
from absl import flags
from absl import logging

import base64
from PIL import Image

from td.environments import Environment, environments
from td.environments.webdev import HTML
from td.learning.tokenizer import Tokenizer
from td.learning.gpt import TreeDiffusion, TransformerConfig
from td.samplers import ConstrainedRandomSampler
from td.learning.constrained_decoding import ar_decoder, sample_model_kv

import pickle
import numpy as np
import io
import os
import uuid
import wandb
import torch

from td.samplers.mutator import random_mutation

flags.DEFINE_string("checkpoint_name", None, "Path to the checkpoint to evaluate")
flags.DEFINE_string("ar_checkpoint_name", None, "Path to the AR checkpoint.")
flags.DEFINE_string("problem_filename", None, "Number of problems to evaluate")
flags.DEFINE_integer("max_steps", 100, "Maximum number of steps to take")
flags.DEFINE_integer("evaluation_batch_size", 16, "Batch size for evaluation")
flags.DEFINE_integer("num_replicas", 1, "Batch size for evaluation")
flags.DEFINE_float("temperature", 1.0, "Temperature for sampling")
flags.DEFINE_string("evaluation_dir", "evals", "Evaluations directory")
flags.DEFINE_bool("wandb", False, "Log to wandb")
flags.DEFINE_string("device", "cuda", "Device to use")

FLAGS = flags.FLAGS

html_dsl = "(Compose (Div margin-top:5px (P '2')) (Div (Junct (Junct margin-right:10% margin-right:24%) background-color:blue) (Compose (P '7') (P '2'))))"


def generate_uuid():
    return str(uuid.uuid4())


def load_model(checkpoint_name, device):
    state = torch.load(checkpoint_name, map_location=device)

    config = state["config"]
    # config["env"] = "html"
    # print(config)

    env_name = config["env"]
    image_model = config["image_model"]
    d_model = config["d_model"]
    n_layers = config["n_layers"]
    num_heads = config["num_heads"]
    max_sequence_length = config["max_sequence_length"]
    target_observation = config["target_observation"]

    # for key, value in config.items():
    # logging.info(f"{key}: {value}")

    env: Environment = environments[env_name]()
    sampler = ConstrainedRandomSampler(env.grammar)
    tokenizer = Tokenizer(
        env.grammar,
        max_token_length=max_sequence_length,
        max_sequence_length=max_sequence_length,
    )

    model = TreeDiffusion(
        TransformerConfig(
            vocab_size=tokenizer.vocabulary_size,
            max_seq_len=tokenizer.max_sequence_length,
            n_layer=n_layers,
            n_head=num_heads,
            n_embd=d_model,
        ),
        input_channels=env.compiled_shape[-1],
        image_model_name=image_model,
    )
    model.load_state_dict(state["model"])
    model.to(device)

    return model, env, tokenizer, sampler, target_observation, config


def create_generator(initial_img):
    logging.info(f"Evaluating {FLAGS.checkpoint_name}")

    if not os.path.exists(FLAGS.evaluation_dir):
        os.makedirs(FLAGS.evaluation_dir)

    local_run_id = generate_uuid()
    logging.info(f"Local run id: {local_run_id}")

    save_filename = os.path.join(FLAGS.evaluation_dir, f"{local_run_id}.pkl")

    td_model, env, tokenizer, sampler, target_observation, _ = load_model(
        FLAGS.checkpoint_name, FLAGS.device
    )
    # print(f"env: {env}")
    # ar_model, _, ar_tokenizer, _, ar_to, ar_config = load_model(
    #     FLAGS.ar_checkpoint_name, FLAGS.device
    # )

    config = {
        "notes": "td-eval",
        "temperature": FLAGS.temperature,
        "max_steps": FLAGS.max_steps,
        "evaluation_batch_size": FLAGS.evaluation_batch_size,
        "checkpoint_name": FLAGS.checkpoint_name,
        "local_run_id": local_run_id,
        "ar_checkpoint_name": FLAGS.ar_checkpoint_name,
        "num_replicas": FLAGS.num_replicas,
    }

    # if wandb:
    #     wandb.init(
    #         project="tree-diffusion",
    #         config=config,
    #     )

    # with open(FLAGS.problem_filename, "rb") as f:
    # target_expressions = ["(- (+ (Quad 4 0 F 4 G) (Quad C 0 F 4 G)) (Circle 1 2 1))"]
    # target_expressions = ["(Arrange h (Rectangle 9 2 blue red 0 -4 +0) (Rectangle 9 2 blue red 0 +4 +0) 0)"]
    # target_expressions = [
    #     "(Arrange v (Ellipse 9 9 red none 0 +0 +0) (Arrange v (Ellipse 7 7 orange none 0 +0 +0) (Arrange v (Ellipse 5 5 yellow none 0 +0 +0) (Ellipse 3 3 green none 0 +0 +0) 3) 2) 1)"

    # target_expressions = [html_dsl]

    # hard = ["(+ (- (Circle 8 6 8) (Circle 5 8 8)) (- (Circle 2 9 A) (Quad 9 A 2 2 H)))"]
    # easy = ["(+ (- (Circle 8 6 8) (Circle 5 8 8)) (Circle 2 9 A))"]

    sampler = ConstrainedRandomSampler(env.grammar)
    expression = sampler.sample(
        env.grammar.sample_start_symbol, min_primitives=1, max_primitives=12
    )
    target_expressions = [expression]

    target_images = np.array(
        [
            env.compile(e) if not target_observation else env.compile_observation(e)
            for e in target_expressions
        ]
    )

    target_images_torch = (
        torch.tensor(target_images).to(FLAGS.device).float().permute(0, 3, 1, 2)
    )

    steps_to_solve = np.zeros(len(target_expressions)) + np.inf

    problem_i = 0
    logging.info(f"Problem {problem_i + 1} / {len(target_expressions)} ...")

    target_image_torch = target_images_torch[problem_i].unsqueeze(0)
    batch_targets = target_image_torch.repeat(FLAGS.num_replicas, 1, 1, 1)

    initial_expression = target_expressions[0]

    num_mutations = 4
    for _ in range(num_mutations):
        mutation = random_mutation(initial_expression, env.grammar, sampler)
        initial_expression = mutation.apply(initial_expression)

    initial_expressions = [
        initial_expression
        # sampler.sample(
        #     env.grammar.sample_start_symbol, min_primitives=1, max_primitives=12
        # )
    ]

    current_expressions = [x for x in initial_expressions]
    current_images = np.array([env.compile(e) for e in current_expressions])
    logging.info(f"shape {current_images.shape}")

    if steps_to_solve[problem_i] < np.inf:
        logging.info(f"Steps to solve: {steps_to_solve[problem_i]}")
        current_solve_rate = np.sum(steps_to_solve < np.inf) / (problem_i + 1)
        logging.info(f"Solve rate: {current_solve_rate * 100:.2f}%")
        with open(save_filename, "wb") as f:
            pickle.dump(
                {
                    "steps_to_solve": steps_to_solve,
                },
                f,
            )

    current_steps = len(current_images)
    values = [-np.inf]

    def step():
        nonlocal current_steps
        nonlocal current_expressions
        nonlocal values
        nonlocal current_images

        yield (target_expressions, target_images)
        yield (current_expressions, current_images)
        for step_i in range(FLAGS.max_steps):
            logging.info(f"Step {step_i} / {FLAGS.max_steps} ... {max(values)}")
            mutations = sample_model_kv(
                td_model,
                env,
                tokenizer,
                current_expressions,
                batch_targets,
                temperature=FLAGS.temperature,
            )

            current_expressions = [
                m.apply(e) for m, e in zip(mutations, current_expressions)
            ]
            try:
                current_images = np.array([env.compile(e) for e in current_expressions])
            except:
                print("current expressions:")
                print(current_expressions)
                # raise ValueError("Error in current expressions")
                continue

            yield (current_expressions, current_images)

            for image_i in range(len(current_images)):
                if env.goal_reached(current_images[image_i], target_images[problem_i]):
                    steps_to_solve[problem_i] = current_steps + image_i + 1
                    print("Goal reached")
                    break
                values.append(
                    env._goal_checker.goal_reached_value(
                        current_images[image_i], target_images[problem_i]
                    )
                )

            current_steps += len(current_images)

            if steps_to_solve[problem_i] < np.inf:
                break

            logging.info(f"Max val: {max(values)}")
            logging.info(f"Steps to solve: {steps_to_solve[problem_i]}")
            current_solve_rate = np.sum(steps_to_solve < np.inf) / (problem_i + 1)
            logging.info(f"Solve rate: {current_solve_rate * 100:.2f}%")
            with open(save_filename, "wb") as f:
                pickle.dump(
                    {
                        "steps_to_solve": steps_to_solve,
                    },
                    f,
                )

    return step


def main(argv):
    # import os
    # from td.environments.webdev import HTML, HTMLCompiler

    # html = HTML()
    # compiler = HTMLCompiler()
    # print("main")
    step_generator = create_generator(argv)
    visualize(step_generator)
    # tries path
    # tries_path = "/Users/nathanvogt/tree-diffusion/scripts/tries"
    # starting_idx = (
    #     max([int(x) for x in os.listdir(tries_path)]) if os.listdir(tries_path) else 0
    # )
    # for current_image, current_expression in image_generator():
    #     html_expression = compiler.semi_compile(
    #         html.grammar.parse(current_expression[0])
    #     )
    #     starting_idx += 1
    #     current_dir = os.path.join(tries_path, str(starting_idx))
    #     os.mkdir(current_dir)
    #     import matplotlib.pyplot as plt

    #     plt.imsave(os.path.join(current_dir, "image.png"), current_image[0])
    #     np.save(os.path.join(current_dir, "image.npy"), current_image)
    #     with open(os.path.join(current_dir, "expression.txt"), "w") as f:
    #         f.write(current_expression[0])
    #     with open(os.path.join(current_dir, "html_expression.txt"), "w") as f:
    #         f.write(str(html_expression))


if __name__ == "__main__":
    app.run(main)
