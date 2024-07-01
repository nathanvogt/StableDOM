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
<html>
<head>
</head>
<body>
<div style=""></div>
<div style="border-radius: 1px; display: flex;"></div>
<div style=""></div>
<div style=""></div>
</body>
</html>
"""

    expr = sampler.sample(
        grammar.sample_start_symbol, min_primitives=1, max_primitives=20
    )
    # print(expr)
    # mutation = random_mutation(program, grammar, sampler)
    # print(mutation)


if __name__ == "__main__":
    main()
