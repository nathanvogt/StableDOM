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


def print_some_batches(batch_size):
    dataset = TreeDiffusionDataset(
        batch_size=batch_size,
        env_name="htmlcss",
        min_steps=1,
        max_steps=4,
        max_sequence_length=3000,
        min_primitives=2,
        max_primitives=10,
        sample_min_primitives=10,
        sample_max_primitives=32,
        selection_max_primitives=16,
        replacement_max_primitives=16,
        path_max_primitives=8,
        forward_mode="path",
        target_observation=False,
        current_observation=False,
        random_mix=0.2,
        premade_sample_mix=0.25
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

def main():
    print_some_batches(batch_size=2)

if __name__ == "__main__":
    main()
