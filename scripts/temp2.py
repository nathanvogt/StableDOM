import os


tries_path = "/Users/nathanvogt/tree-diffusion/scripts/tries"

idx_oder = [
    # 19,
    # 2,
    # 3,
    # 4,
    # 5,
    # 7,
    # 8,
    # 12,
    # 11,
    # 40,
    # 41,
    # 39,
    # 37,
    # 47,
    # 48,
    # 36,
    # 30,
    # 29,
    # 28,
    # 26,
    # 25,
    # 23,
    # 22,
    100,
    98,
    96,
    92,
    54,
    38,
    37,
    34,
    90,
    91,
    88,
    87,
    86,
    85,
    82,
    81,
    80,
    79,
    75,
    71,
    70,
    67,
    64,
]

from td.environments.webdev import HTML, HTMLCompiler

html = HTML()
compiler = HTMLCompiler()
expressions = []
html_expressions = []
for i in idx_oder:
    expression = f"{open(os.path.join(tries_path, str(i), 'expression.txt')).read()}"
    expressions.append(expression)
    html_expression = (
        f"'{open(os.path.join(tries_path, str(i), 'html_expression.txt')).read()}'"
    )
    html_expression = compiler.semi_compile(html.grammar.parse(expression))
    html_expressions.append(html_expression)

print(expressions)
print("\n")
print(html_expressions)
