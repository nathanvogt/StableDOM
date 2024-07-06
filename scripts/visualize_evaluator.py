from train import TreeDiffusionDataset
from td.environments.webdev import HTML
from td.environments.csg2da import CSG2DA
import math
import matplotlib.pyplot as plt
from td.samplers import ConstrainedRandomSampler
from td.learning.tokenizer import Tokenizer
from td.learning.evaluation import OneStepEvaluator
import numpy as np
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


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
        expression = sampler.sample(
            env.grammar.sample_start_symbol,
        )
        print(f"Expression {i+1}: {expression}")
        if display:
            img = env.compile(str(expression))
            axes[i].imshow(img)
            axes[i].axis("off")
            axes[i].set_title(f"Expr {i+1}", fontsize=10)
    if display:
        plt.tight_layout()
        plt.show()


def print_some_batches(batch_size):
    dataset = TreeDiffusionDataset(
        batch_size=batch_size,
        env_name="htmlcss",
        min_steps=1,
        max_steps=5,
        max_sequence_length=2048,
        min_primitives=1,
        max_primitives=8,
        sample_min_primitives=1,
        sample_max_primitives=32,
        selection_max_primitives=10,
        replacement_max_primitives=10,
        path_max_primitives=4,
        forward_mode="path",
        target_observation=False,
        current_observation=False,
        random_mix=0.2,
    )
    start_time = time.time()
    batch = next(iter(dataset))
    end_time = time.time()
    print(f"Time to load batch: {end_time - start_time:.4f} seconds")
    _, _, target_images, mutated_images, _ = batch
    fig = plt.figure(figsize=(10, 5 * batch_size))
    gs = GridSpec(batch_size, 2, figure=fig)
    for i in range(batch_size):
        target_img = np.transpose(target_images[i], (1, 2, 0))
        mutated_img = np.transpose(mutated_images[i], (1, 2, 0))
        ax1 = fig.add_subplot(gs[i, 0])
        ax1.imshow(target_img)
        ax1.set_title(f"Target {i+1}")
        ax1.axis("off")
        ax2 = fig.add_subplot(gs[i, 1])
        ax2.imshow(mutated_img)
        ax2.set_title(f"Mutated {i+1}")
        ax2.axis("off")
    plt.tight_layout()
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    fig.set_size_inches(10, 5 * batch_size)
    plt.show()


def time_batch_loading(env_class, num_batches=10):
    start_time = time.time()

    env = env_class()
    dataset = TreeDiffusionDataset(
        batch_size=1,
        env=env,
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
    # print_some_samples()
    print_some_batches(batch_size=4)


if __name__ == "__main__":
    main()
