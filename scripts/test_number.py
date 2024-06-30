from lark import Token
from td.environments.webdev import HTML
from td.learning.tokenizer import Tokenizer
from td.samplers import ConstrainedRandomSampler

max_sequence_length = 1024


def main():

    env = HTML()
    grammar = env.grammar
    print(grammar.vocabulary)
    sampler = ConstrainedRandomSampler(grammar)
    number_symbol = grammar.names_to_symbols["number"]
    sampled = sampler.sample(number_symbol)
    print(f"sampled: {sampled}")


if __name__ == "__main__":
    main()
