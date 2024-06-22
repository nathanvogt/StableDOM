from lark import Transformer, Tree, v_args
from td.grammar import Compiler, Grammar
from td.environments.environment import Environment
from td.environments.goal_checker import GaussianImageGoalChecker

from html2image import Html2Image

from PIL import Image
import numpy as np
import os

grammar_spec = r"""

    compose: element element
    element: paragraph | div | compose
    paragraph: "(" "P" "'" text "'" ")"
    div: "(" "Div" element ")"
    //TEXT: /[a-zA-Z0-9\s]+/
    text: "lorem ipsum" -> loremipsum

    style: "(" "Style" style_element ")"
    style_junct: style_element style_element
    style_element: style_pair | style_junct
    style_border: "border" ":" size unit color
    style_width: "width" ":" size unit
    style_height: "height" ":" size unit
    style_pair: style_border | style_width | style_height

    color: "red" -> red | "blue" -> blue
    size: "12" -> twelve | "24" -> twentyfour | "36" -> thirtysix
    unit: "px" -> px

    %ignore /[\t \n\f\r]+/  // Ignore whitespace
"""

_SCREEN_WIDTH = 224
_SCREEN_HEIGHT = 224


class HTMLTransformer(Transformer):
    @v_args(inline=True)
    def text(self, text):
        return text.strip()

    def style_border(self, children):
        (size, unit, color) = children
        return f"border: {size}{unit} solid {color}"

    def style_width(self, children):
        (width, unit) = children
        return f"width: {width}{unit}"

    def style_height(self, children):
        (height, unit) = children
        return f"height: {height}{unit}"

    def style_pair(self, children):
        return children[0]

    def style_junct(self, children):
        return "; ".join(children)

    def style_element(self, children):
        return children[0]

    def style(self, children):
        s = children[0]
        return f"style='{s}'"

    def compose(self, children):
        return "".join(children)

    def div(self, children):
        if children and len(children):
            style = (
                children[0]
                if len(children[0]) >= len("style")
                and children[0][: len("style")] == "style"
                else ""
            )
            elements = children if style == "" else children[1:]
            return f"<div {style}>" + "".join(elements) + "</div>"
        return "<div></div>"

    def paragraph(self, children):
        text = children[0]
        return f"<p>{text}</p>"

    def element(self, children):
        return children[0]

    def body(self, children):
        return "<body style='background-color: white'>" + "".join(children) + "</body>"

    def html(self, children):
        (body,) = children
        return f"<html>{body}</html>"

    def twelve(self, _):
        return 12

    def twentyfour(self, _):
        return 24

    def thirtysix(self, _):
        return 36

    def red(self, _):
        return "red"

    def blue(self, _):
        return "blue"

    def px(self, _):
        return "px"

    def loremipsum(self, _):
        return "heheheloremipsumhehehehe"


class HTMLCompiler(Compiler):
    def __init__(self):
        super().__init__()
        self._expression_to_html = HTMLTransformer()
        self._hti = Html2Image()
        self.temp_img_path = "temp.png"

    def compile(self, expression: Tree):
        content = self._expression_to_html.transform(expression)
        html = f"<html><body>{content}</body></html>"
        self._hti.screenshot(
            html_str=html,
            save_as=self.temp_img_path,
            size=(_SCREEN_WIDTH, _SCREEN_HEIGHT),
        )
        img = Image.open(self.temp_img_path)
        try:
            os.remove(self.temp_img_path)
        except FileNotFoundError:
            print("File not found")

        img_rgb = img.convert("RGB")
        img_array = np.array(img_rgb)
        return img_array / 255.0


class HTML(Environment):
    def __init__(self):
        super().__init__()
        self._grammar = Grammar(
            grammar_spec, start="element", primitives=["paragraph", "div"]
        )
        self._compiler = HTMLCompiler()
        self._goal_checker = GaussianImageGoalChecker(self.compiled_shape)

    @property
    def grammar(self) -> Grammar:
        return self._grammar

    @property
    def compiler(self) -> Compiler:
        return self._compiler

    @property
    def compiled_shape(self):
        return _SCREEN_WIDTH, _SCREEN_HEIGHT, 3

    @classmethod
    def name(cls):
        return "html"

    def goal_reached(self, compiledA, compiledB):
        return self._goal_checker.goal_reached(compiledA, compiledB)
