from generate_vis import visualize
from absl import app
from absl import flags
from absl import logging

import base64
from PIL import Image

from td.environments import Environment, environments
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

# DEFINE_string("checkpoint_name", None, "Path to the checkpoint to evaluate")
# DEFINE_string("ar_checkpoint_name", None, "Path to the AR checkpoint.")
# DEFINE_string("problem_filename", None, "Number of problems to evaluate")
# DEFINE_integer("max_steps", 100, "Maximum number of steps to take")
# DEFINE_integer("evaluation_batch_size", 16, "Batch size for evaluation")
# DEFINE_integer("num_replicas", 1, "Batch size for evaluation")
# DEFINE_float("temperature", 1.0, "Temperature for sampling")
# DEFINE_string("evaluation_dir", "evals", "Evaluations directory")
# DEFINE_bool("wandb", True, "Log to wandb")
# DEFINE_string("device", "cuda", "Device to use")

checkpoint_name = "assets/td_csg2da.pt"
ar_checkpoint_name = "assets/ar_csg2da.pt"
problem_filename = "assets/csg2da_test_set.pkl"
max_steps = 100
evaluation_batch_size = 16
num_replicas = 1
temperature = 1.0
evaluation_dir = "evals"
wandb_log = True
device = "cpu"




class CPU_Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == "torch.storage" and name == "_load_from_bytes":
            return lambda b: torch.load(io.BytesIO(b), map_location="cpu")
        else:
            return super().find_class(module, name)


def generate_uuid():
    return str(uuid.uuid4())


def load_model(checkpoint_name, device):
    with open(checkpoint_name, "rb") as f:
        if torch.cuda.is_available():
            state = pickle.load(f)
        else:
            state = CPU_Unpickler(f).load()

    config = state["config"]

    env_name = config["env"]
    image_model = config["image_model"]
    d_model = config["d_model"]
    n_layers = config["n_layers"]
    num_heads = config["num_heads"]
    max_sequence_length = config["max_sequence_length"]
    target_observation = config["target_observation"]

    for key, value in config.items():
        logging.info(f"{key}: {value}")

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
    logging.info(f"Evaluating {checkpoint_name}")

    if not os.path.exists(evaluation_dir):
        os.makedirs(evaluation_dir)

    local_run_id = generate_uuid()
    logging.info(f"Local run id: {local_run_id}")

    save_filename = os.path.join(evaluation_dir, f"{local_run_id}.pkl")

    td_model, env, tokenizer, sampler, target_observation, _ = load_model(
        checkpoint_name, device
    )
    ar_model, _, ar_tokenizer, _, ar_to, ar_config = load_model(
        ar_checkpoint_name, device
    )

    config = {
        "notes": "td-eval",
        "temperature": temperature,
        "max_steps": max_steps,
        "evaluation_batch_size": evaluation_batch_size,
        "checkpoint_name": checkpoint_name,
        "local_run_id": local_run_id,
        "ar_checkpoint_name": ar_checkpoint_name,
        "num_replicas": num_replicas,
    }

    if wandb:
        wandb.init(
            project="tree-diffusion",
            config=config,
        )

    with open(problem_filename, "rb") as f:
        target_expressions = ["(+ (- (Circle 8 8 8) (Circle 5 8 8)) (- (Quad 8 8 4 4 H) (Circle 1 8 8)))"]
        # target_expressions = ["(Arrange h (Arrange h (Rectangle 9 2 blue red 0 -4 +0) (Rectangle 9 2 blue red 0 -9 +0) 0) (Rectangle 9 2 blue red 0 +4 +0) 0)"]


    decoded_img = base64.b64decode(initial_img)
    img = Image.open(io.BytesIO(decoded_img))
    target_images = np.array(img)

    target_images_torch = (
        torch.tensor(target_images).to(device).float().permute(0, 3, 1, 2)
    )

    steps_to_solve = np.zeros(len(target_expressions)) + np.inf

    problem_i = 0
    logging.info(f"Problem {problem_i + 1} / {len(target_expressions)} ...")

    target_image_torch = target_images_torch[problem_i].unsqueeze(0)
    # Replicate the target image to create a batch.
    batch_targets = target_image_torch.repeat(num_replicas, 1, 1, 1)

    ar_predictions = ar_decoder(
        ar_model,
        env,
        ar_tokenizer,
        ar_config["num_image_tokens"],
        batch_targets,
        temperature=1.0,
    )

    # initial_expressions = list(set(ar_predictions))[: num_replicas]
    # logging.info(f"Unique AR predictions: {len(initial_expressions)}")
    # while len(initial_expressions) < num_replicas:
    #     initial_expressions.append(sampler.sample(env.grammar.start_symbol))

    initial_expressions = ["(Quad 0 0 0 0 H)"]
    # initial_expressions = ["(Rectangle 0 0 red blue 0 +0 +0)"]

    current_expressions = [x for x in initial_expressions]
    current_images = np.array([env.compile(e) for e in current_expressions])
    logging.info(f"shape {current_images.shape}")

    # Did we already solve the problem?
    # for image_i in range(len(current_images)):
    #     if env.goal_reached(current_images[image_i], target_images[problem_i]):
    #         logging.info(f"Problem already solved")
    #         steps_to_solve[problem_i] = image_i + 1
    #         break

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

    # We've already spent replicas.
    current_steps = len(current_images)
    values = [-np.inf]

    def step():
        nonlocal current_steps
        nonlocal current_expressions
        nonlocal values
        nonlocal current_images
        
        yield (current_expressions, current_images)
        for step_i in range(max_steps):
            logging.info(f"Step {step_i} / {max_steps} ... {max(values)}")
            mutations = sample_model_kv(
                td_model,
                env,
                tokenizer,
                current_expressions,
                batch_targets,
                temperature=temperature,
            )

            current_expressions = [
                m.apply(e) for m, e in zip(mutations, current_expressions)
            ]
            current_images = np.array([env.compile(e) for e in current_expressions])

            yield (current_expressions, current_images)

            for image_i in range(len(current_images)):
                if env.goal_reached(current_images[image_i], target_images[problem_i]):
                    steps_to_solve[problem_i] = current_steps + image_i + 1
                    break
                values.append(
                    env._goal_checker.goal_reached_value(
                        current_images[image_i], target_images[problem_i]
                    )
                )

            current_steps += len(current_images)

            if steps_to_solve[problem_i] < np.inf:
                break
    
            # np_iteration_images = np.array(iteration_images)

            # logging.info(f"Saving images: {np_iteration_images.shape}")
            # np.save("evaluation_output", np_iteration_images)

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

def make_main(update_step, initial_img):
    def main():
        step_generator = create_generator(initial_img)
        for expression, image in step_generator():
            pil_img = Image.fromarray(image.astype(np.uint8))
            buffer = io.BytesIO()
            pil_img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            if update_step: update_step({"expression": expression, "image": img_str})
    return main

def default_main():
    step_generator = create_generator()
    visualize(step_generator)

if __name__ == "__main__":
    app.run(default_main)
