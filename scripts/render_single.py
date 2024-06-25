from td.environments import Environment, environments
import sys
from train import TreeDiffusionDataset
import matplotlib.pyplot as plt
from td.samplers import ConstrainedRandomSampler
from td.learning.tokenizer import Tokenizer
from td.learning.evaluation import OneStepEvaluator
import numpy as np
import time


def main(*args):
    env = environments[args[0]]()
    expression = args[1]
    start_time = time.time()
    img = env.compile(str(expression))
    end_time = time.time()
    print(f"Time to compile: {end_time - start_time:.4f} seconds")
    plt.imshow(img)
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    main(*sys.argv[1:])
