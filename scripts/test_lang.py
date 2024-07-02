from lark import Token
from td.environments.html import HTMLCSS, HTMLCSSTransformer
from td.learning.tokenizer import Tokenizer
from td.samplers import ConstrainedRandomSampler
from td.samplers.mutator import random_mutation

max_sequence_length = 1024


def main():

    env = HTMLCSS()
    grammar = env.grammar
    transformer = HTMLCSSTransformer()
    sampler = ConstrainedRandomSampler(grammar)
    program = """
<div style= " " > It Which know she your not year... Thus, That we how her that say even? </div> <div style= " " > Some work also then do its Us day a if say! This of this day light some us your? </div>
"""

    # expr = sampler.sample(
    #     grammar.sample_start_symbol, min_primitives=1, max_primitives=20
    # )
    # print(expr)
    mutation = random_mutation(program, grammar, sampler)
    print(f"{mutation=}")
    mutated = mutation.apply(program)
    print(f"{mutated=}")


if __name__ == "__main__":
    main()
