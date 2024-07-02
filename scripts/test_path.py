from lark import Token
from td.environments.html import HTMLCSS, HTMLCSSTransformer
from td.learning.tokenizer import Tokenizer
from td.samplers import ConstrainedRandomSampler
from td.samplers.mutator import random_mutation, find_path, one_step_path_mutations

max_sequence_length = 1024


def main():

    env = HTMLCSS()
    grammar = env.grammar
    transformer = HTMLCSSTransformer()
    sampler = ConstrainedRandomSampler(grammar)

    source = """
<html>
<head>
</head>
<body>
    <div style=""></div>
</body>
</html>
"""

    target = """
<html>
<head>
</head>
<body>
    <div style="border: 1px solid #FF0000; border-radius: 2px; display: flex;"></div>
</body>
</html>
"""
    path = find_path(source, target, grammar, sampler)
    print(path)


if __name__ == "__main__":
    main()
