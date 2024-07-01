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
    program = """
<html>
<head>
</head>
<body>
<div>
<p>hello world</p>
</div>
</body>
</html>
"""
    parsed = grammar.parse(program)
    # print(parsed.pretty())
    transformed = transformer.transform(parsed)
    print(transformed)


if __name__ == "__main__":
    main()
