from train import TreeDiffusionDataset
from td.environments.webdev import HTML
from td.environments.csg2da import CSG2DA
import matplotlib.pyplot as plt
from td.samplers import ConstrainedRandomSampler
from td.learning.tokenizer import Tokenizer
from td.learning.evaluation import OneStepEvaluator
import numpy as np
import time


def print_some_samples():
    display = True
    device = "cpu"
    env = HTML()
    sampler = ConstrainedRandomSampler(env.grammar)
    if display:
        _, axes = plt.subplots(3, 3, figsize=(15, 15))
        axes = axes.flatten()
    num_samples = 6
    for i in range(num_samples):
        expression = sampler.sample(env.grammar.sample_start_symbol, max_primitives=25)
        print(f"Expression {i+1}: {expression}")
        if display:
            img = env.compile(str(expression))
            axes[i].imshow(img)
            axes[i].axis("off")
            axes[i].set_title(f"Expr {i+1}", fontsize=10)
    if display:
        plt.tight_layout()
        plt.show()


def time_batch_loading(env_class, num_batches=10):
    start_time = time.time()

    env = env_class()
    dataset = TreeDiffusionDataset(
        batch_size=1,
        env_name=env.name(),
        min_steps=1,
        max_steps=5,
        max_sequence_length=512,
        min_primitives=4,
        max_primitives=8,
        forward_mode="path",
        target_observation=False,
        current_observation=False,
        random_mix=0.2,
    )

    count = 0
    for batch in dataset:
        if count == num_batches:
            break
        count += 1

    end_time = time.time()
    return end_time - start_time


def compare_env_loading_times(num_batches=10, num_runs=5):
    html_times = []
    csg2da_times = []

    for _ in range(num_runs):
        html_time = time_batch_loading(HTML, num_batches)
        html_times.append(html_time)

        csg2da_time = time_batch_loading(CSG2DA, num_batches)
        csg2da_times.append(csg2da_time)

    avg_html_time = sum(html_times) / num_runs
    avg_csg2da_time = sum(csg2da_times) / num_runs

    print(
        f"Average time for HTML env ({num_batches} batches, {num_runs} runs): {avg_html_time:.4f} seconds"
    )
    print(
        f"Average time for CSG2DA env ({num_batches} batches, {num_runs} runs): {avg_csg2da_time:.4f} seconds"
    )
    print(f"Difference (CSG2DA - HTML): {avg_csg2da_time - avg_html_time:.4f} seconds")


def main():
    print_some_samples()


if __name__ == "__main__":
    main()
