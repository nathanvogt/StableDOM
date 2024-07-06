import os
import pickle
import random
import uuid

import numpy as np
import torch
import torch.nn.functional as F
from absl import app, flags, logging
from torch.utils.data import DataLoader

import wandb
from td.data.diffusion_dataset import TreeDiffusionDataset
from td.environments import environments
from td.learning.gpt import TransformerConfig, TreeDiffusion
from td.learning.tokenizer import Tokenizer
from td.learning.evaluation import OneStepEvaluator
from td.samplers import ConstrainedRandomSampler


FLAGS = flags.FLAGS
flags.DEFINE_integer("batch_size", 8, "Batch size")
flags.DEFINE_integer("print_every", 1000, "Print every")
flags.DEFINE_integer("test_every", 10000, "Test every")
flags.DEFINE_integer("training_steps", -1, "Training steps")
flags.DEFINE_string("checkpoint_dir", "checkpoints", "Checkpoint directory")
flags.DEFINE_integer("checkpoint_steps", 10000, "Checkpoint steps")
flags.DEFINE_integer("num_workers", 8, "Number of workers for data loading")
flags.DEFINE_integer("max_steps", 5, "Minimum number of steps")
flags.DEFINE_float("learning_rate", 3e-4, "Learning rate")
flags.DEFINE_bool("wandb", True, "Log to wandb")
flags.DEFINE_string("env", "htmlcss", "Environment to use")
flags.DEFINE_integer("num_test_expressions", 32, "Number of test expressions")
flags.DEFINE_integer("num_test_steps", 10, "Number of test steps")
flags.DEFINE_integer("max_sequence_length", 2048, "Maximum sequence length")
flags.DEFINE_integer("min_primitives", 2, "Minimum number of primitives")
flags.DEFINE_integer("max_primitives", 8, "Maximum number of primitives")
flags.DEFINE_integer("sample_min_primitives", 1, "Minimum number of primitives")
flags.DEFINE_integer("sample_max_primitives", 32, "Maximum number of primitives")
flags.DEFINE_integer("selection_max_primitives", 16, "Maximum number of primitives")
flags.DEFINE_integer("replacement_max_primitives", 16, "Maximum number of primitives")
flags.DEFINE_integer("path_max_primitives", 8, "Maximum number of primitives")
flags.DEFINE_integer("n_layers", 6, "Number of layers")
flags.DEFINE_integer("d_model", 512, "Model dimension")
flags.DEFINE_integer("num_heads", 32, "Number of heads")
flags.DEFINE_string("device", "cuda", "Device to use")
flags.DEFINE_string("image_model", "nf_resnet26", "Vision model to use")
flags.DEFINE_enum(
    "forward_mode",
    "path",
    ["normal", "guards", "guards_full", "path"],
    "Forward mode",
)
flags.DEFINE_string("resume_from", None, "Resume from checkpoint")
flags.DEFINE_bool(
    "target_observation", False, "Use observation compiler for target image."
)
flags.DEFINE_bool(
    "current_observation", False, "Use observation compiler for current image."
)
flags.DEFINE_bool("current_image", True, "Include current image, for ablation study.")
flags.DEFINE_float(
    "random_mix",
    0.2,
    "Probability of sampling a completely random starting expression.",
)


def loss_fn(model, batch):
    tokens, mask, target_images, mutated_images, steps = batch

    if not FLAGS.current_image:
        mutated_images = mutated_images * 0.0

    logits = model(tokens, target_images, mutated_images)

    logits = logits[:, :-1]
    targets = tokens[:, 1:]
    mask = mask[:, 1:]

    loss = F.cross_entropy(
        logits.reshape(-1, logits.size(-1)), targets.reshape(-1), reduction="none"
    )
    loss = loss.reshape(targets.shape)
    loss = (loss * mask).sum() / mask.sum()

    first_one = torch.argmax(mask, axis=-1)
    ground_truth_pos_tokens = targets[torch.arange(targets.shape[0]), first_one]
    predictions = logits.argmax(axis=-1)
    predicted_pos_tokens = predictions[torch.arange(predictions.shape[0]), first_one]
    position_accuracy = (ground_truth_pos_tokens == predicted_pos_tokens).float().mean()

    return loss, (position_accuracy,)


def generate_uuid():
    return str(uuid.uuid4())


def batch_to_torch(batch, device="cpu"):
    tokens, mask, target_images, mutated_images, steps = batch
    res = (
        tokens.to(device).long(),
        mask.to(device).float(),
        target_images.to(device).float(),
        mutated_images.to(device).float(),
        steps.to(device).long(),
    )
    return res


def main(argv):
    env = environments[FLAGS.env]()
    sampler = ConstrainedRandomSampler(env.grammar)
    tokenizer = Tokenizer(
        env.grammar,
        max_token_length=FLAGS.max_sequence_length,
        max_sequence_length=FLAGS.max_sequence_length,
    )
    one_step_evaluator = OneStepEvaluator(
        env,
        sampler,
        tokenizer,
        num_problems=FLAGS.num_test_expressions,
        device=FLAGS.device,
        evaluation_batch_size=FLAGS.batch_size,
        target_observation=FLAGS.target_observation,
        sample_min_primitives=FLAGS.sample_min_primitives,
        sample_max_primitives=FLAGS.sample_max_primitives,
        selection_max_primitives=FLAGS.selection_max_primitives,
        replacement_max_primitives=FLAGS.replacement_max_primitives,
    )

    random.seed(1)

    local_run_id = FLAGS.resume_from or generate_uuid()
    checkpoint_dir = (
        os.path.join(FLAGS.checkpoint_dir, local_run_id)
        if FLAGS.checkpoint_dir
        else None
    )
    step = 0

    config = {
        "notes": "",
        "batch_size": FLAGS.batch_size,
        "learning_rate": FLAGS.learning_rate,
        "env": FLAGS.env,
        "max_steps": FLAGS.max_steps,
        "local_run_id": local_run_id,
        "max_sequence_length": FLAGS.max_sequence_length,
        "max_primitives": FLAGS.max_primitives,
        "min_primitives": FLAGS.min_primitives,
        "sample_min_primitives": FLAGS.sample_min_primitives,
        "sample_max_primitives": FLAGS.sample_max_primitives,
        "selection_max_primitives": FLAGS.selection_max_primitives,
        "replacement_max_primitives": FLAGS.replacement_max_primitives,
        "path_max_primitives": FLAGS.path_max_primitives,
        "n_layers": FLAGS.n_layers,
        "d_model": FLAGS.d_model,
        "num_heads": FLAGS.num_heads,
        "image_model": FLAGS.image_model,
        "forward_mode": FLAGS.forward_mode,
        "target_observation": FLAGS.target_observation,
        "current_observation": FLAGS.current_observation,
        "current_image": FLAGS.current_image,
        "random_mix": FLAGS.random_mix,
    }

    if FLAGS.wandb:
        wandb.init(
            project="stabledom2",
            config=config,
        )

    model = TreeDiffusion(
        TransformerConfig(
            vocab_size=tokenizer.vocabulary_size,
            max_seq_len=tokenizer.max_sequence_length,
            n_layer=FLAGS.n_layers,
            n_head=FLAGS.num_heads,
            n_embd=FLAGS.d_model,
        ),
        input_channels=env.compiled_shape[-1],
        image_model_name=FLAGS.image_model,
    ).to(FLAGS.device)

    if os.path.exists(checkpoint_dir):
        checkpoint_files = [
            f
            for f in os.listdir(checkpoint_dir)
            if f.endswith(".pt") and f.startswith(f"{FLAGS.env}_step_")
        ]
        if checkpoint_files:
            latest_checkpoint = max(
                checkpoint_files, key=lambda x: int(x.split("_")[-1].split(".")[0])
            )
            checkpoint_filename = os.path.join(checkpoint_dir, latest_checkpoint)
            with open(checkpoint_filename, "rb") as f:
                state = pickle.load(f)
                if "model" in state:
                    model.load_state_dict(state["model"])
                else:
                    model.load_state_dict(state)
            step = int(latest_checkpoint.split("_")[-1].split(".")[0])
            logging.info(
                f"Loaded checkpoint from {checkpoint_filename}, starting at step {step}"
            )

    optimizer = torch.optim.Adam(model.parameters(), lr=FLAGS.learning_rate)

    logging.info("Starting to train!")

    if (
        checkpoint_dir
        and FLAGS.checkpoint_steps > 0
        and not os.path.exists(checkpoint_dir)
    ):
        logging.info(
            f"Local run ID: {local_run_id}, saving checkpoints to {checkpoint_dir}"
        )
        os.makedirs(checkpoint_dir)

    batch_metrics = []

    batch_size = FLAGS.batch_size
    env_name = FLAGS.env
    max_steps = FLAGS.max_steps
    max_sequence_length = FLAGS.max_sequence_length
    min_primitives = FLAGS.min_primitives
    max_primitives = FLAGS.max_primitives

    dataset = TreeDiffusionDataset(
        batch_size=batch_size,
        env_name=FLAGS.env,
        min_steps=1,
        max_steps=max_steps,
        max_sequence_length=max_sequence_length,
        min_primitives=min_primitives,
        max_primitives=max_primitives,
        forward_mode=FLAGS.forward_mode,
        target_observation=FLAGS.target_observation,
        current_observation=FLAGS.current_observation,
        random_mix=FLAGS.random_mix,
    )

    dataloader = DataLoader(dataset, batch_size=None, num_workers=FLAGS.num_workers)
    model.train()
    for batch in dataloader:
        batch = batch_to_torch(batch, FLAGS.device)
        loss, aux = loss_fn(model, batch)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        position_accuracy = aux[0]

        batch_metrics.append((loss, position_accuracy))

        if step % FLAGS.print_every == FLAGS.print_every - 1:
            metrics = np.mean(
                np.array(torch.tensor(batch_metrics).detach().cpu()), axis=0
            )
            mean_loss, mean_position_accuracy = metrics
            logging.info(
                f"Step {step + 1}, Loss: {mean_loss:.4f}, Position Accuracy: {mean_position_accuracy:.2f}"
            )

            if FLAGS.wandb:
                wandb.log(
                    {
                        "loss": mean_loss,
                        "position_accuracy": mean_position_accuracy,
                    },
                    step=step + 1,
                )

            batch_metrics.clear()

        if FLAGS.test_every > 0 and step % FLAGS.test_every == FLAGS.test_every - 1:
            eval_result = one_step_evaluator.evaluate(model, progress_bar=False)

            logging.info(
                f"Step {step + 1}, Goal reached: {eval_result.goal_reached:.2f}, Error rate: {eval_result.error_rate:.2f}"
            )

            if FLAGS.wandb:
                wandb.log(
                    {
                        "onestep_goal_reached": eval_result.goal_reached,
                        "onestep_error_rate": eval_result.error_rate,
                    },
                    step=step + 1,
                )

            model.train()

        if (
            checkpoint_dir
            and FLAGS.checkpoint_steps > 0
            and step % FLAGS.checkpoint_steps == FLAGS.checkpoint_steps - 1
        ):
            checkpoint_filename = os.path.join(
                checkpoint_dir, f"{env_name}_step_{step + 1}.pt"
            )
            if os.path.exists(checkpoint_filename):
                logging.warning(
                    f"Checkpoint file {checkpoint_filename} already exists, skipping."
                )
            else:
                with open(checkpoint_filename, "wb") as f:
                    pickle.dump({"model": model.state_dict(), "config": config}, f)
                logging.info(f"Checkpointed state to {checkpoint_filename}")

        step += 1

        if FLAGS.training_steps > 0 and step >= FLAGS.training_steps:
            break


if __name__ == "__main__":
    app.run(main)
