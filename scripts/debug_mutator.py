from train import TreeDiffusionDataset
from td.environments.webdev import HTML
from td.environments.csg2da import CSG2DA
import matplotlib.pyplot as plt
from td.samplers import ConstrainedRandomSampler
from td.learning.tokenizer import Tokenizer
from td.learning.evaluation import OneStepEvaluator
import numpy as np
import time
from td.samplers.mutator import (
    forward_process,
    forward_process_with_path,
    random_mutation,
)


def get_rand_mutation():
    html = HTML()
    num_steps = 4
    expression = "(Div (Junct margin-top:9% margin-right:auto) (Div (Junct margin-right:auto margin-top:auto) (P '50')))"
    sampler = ConstrainedRandomSampler(html.grammar)
    mutation = random_mutation(expression, html.grammar, sampler)
    print(f"Original expression: {expression}")
    print(f"Mutated expression: {mutation}")


def some_forward_steps():
    html = HTML()
    num_steps = 4
    expression = "(Div (Junct margin-top:9% margin-right:auto) (Div (Junct margin-right:auto margin-top:auto) (P '50')))"
    sampler = ConstrainedRandomSampler(html.grammar)
    expr, rev_mut = forward_process(expression, num_steps, html.grammar, sampler)
    print(f"Original expression: {expression}")
    print(f"Mutated expression: {expr}")
    print(f"Reverse mutation: {rev_mut}")


def the_forward_process():
    html = HTML()
    num_steps = 4
    expression = "(Div (Junct margin-top:9% margin-right:auto) (Div (Junct margin-right:auto margin-top:auto) (P '50')))"
    sampler = ConstrainedRandomSampler(html.grammar)
    expr, rev_mut = forward_process_with_path(
        expression, num_steps, html.grammar, sampler, p_random=0
    )
    print(f"Original expression: {expression}")
    print(f"Mutated expression: {expr}")
    print(f"Reverse mutation: {rev_mut}")


def main():
    the_forward_process()


if __name__ == "__main__":
    main()
