from td.environments import Environment, environments
import sys
from train import TreeDiffusionDataset
import matplotlib.pyplot as plt
from td.samplers import ConstrainedRandomSampler
from td.learning.tokenizer import Tokenizer
from td.learning.evaluation import OneStepEvaluator
import numpy as np


def main(*args):
    env = environments[args[0]]()
    expression = args[1]
    print(expression)
    img = env.compile(str(expression))
    plt.imshow(img)
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    main(*sys.argv[1:])
