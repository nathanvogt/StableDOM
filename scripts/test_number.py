from lark import Token
from td.environments.webdev import HTML
from td.learning.tokenizer import Tokenizer
from td.samplers import ConstrainedRandomSampler
from td.samplers.mutator import random_mutation

max_sequence_length = 1024


def main():

    env = HTML()
    grammar = env.grammar
    sampler = ConstrainedRandomSampler(grammar)
    # sample a random expression
    expr = sampler.sample(grammar.sample_start_symbol)
    print(expr)
    # expr = "(Div margin-left:4px (P 'hello world'))"
    # parsed = grammar.parse(expr)
    # print(parsed)
    # mutation = random_mutation(expr, grammar, sampler)
    # print(mutation)


if __name__ == "__main__":
    main()
