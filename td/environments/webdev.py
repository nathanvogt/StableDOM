from lark import Transformer, Tree, v_args
from td.grammar import Compiler, Grammar
from td.environments.environment import Environment
from td.environments.goal_checker import GaussianImageGoalChecker
import imgkit
from IPython.display import Image
from io import BytesIO
from PIL import Image as PILImage
import numpy as np

from html2image import Html2Image

from PIL import Image
import numpy as np

grammar_spec = r"""

    compose: element element
    element: paragraph | div | compose
    paragraph: "(" "P" "'" text "'" ")"
    div: "(" "Div" [style] element ")"
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
    size: "4" -> four | "12" -> twelve | "24" -> twentyfour | "36" -> thirtysix
    unit: "px" -> px

    %ignore /[\t \n\f\r]+/  // Ignore whitespace
"""

_SCREEN_WIDTH = 224 * 4
_SCREEN_HEIGHT = 224 * 2


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

    def four(self, _):
        return 4

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


def resize_image(image, new_width, new_height):
    original_height, original_width, _ = image.shape

    height_ratio = new_height / original_height
    width_ratio = new_width / original_width
    resize_ratio = min(height_ratio, width_ratio)

    intermediate_height = int(original_height * resize_ratio)
    intermediate_width = int(original_width * resize_ratio)

    resized_image = np.zeros(
        (intermediate_height, intermediate_width, 3), dtype=image.dtype
    )
    for i in range(intermediate_height):
        for j in range(intermediate_width):
            x = int(j / resize_ratio)
            y = int(i / resize_ratio)
            resized_image[i, j, :] = image[y, x, :]

    final_image = np.zeros((new_height, new_width, 3), dtype=image.dtype)
    start_x = (new_width - intermediate_width) // 2
    start_y = (new_height - intermediate_height) // 2

    final_image[
        start_y : start_y + intermediate_height,
        start_x : start_x + intermediate_width,
        :,
    ] = resized_image

    return final_image


class HTMLCompiler(Compiler):
    def __init__(self):
        super().__init__()
        self._expression_to_html = HTMLTransformer()
        self._hti = Html2Image()
        self.temp_img_path = "temp.png"

    def compile(self, expression: Tree):
        content = self._expression_to_html.transform(expression)
        html = f"<html><body>{content}</body></html>"
        img_raw = imgkit.from_string(html, False, options={"format": "png"})
        image = PILImage.open(BytesIO(img_raw))
        if image.mode != "RGB":
            image = image.convert("RGB")
        desired_width = _SCREEN_WIDTH
        desired_height = _SCREEN_HEIGHT
        image = image.resize((desired_width, desired_height), PILImage.LANCZOS)
        image_array = np.array(image)
        assert image_array.shape == (_SCREEN_HEIGHT, _SCREEN_WIDTH, 3)
        return image_array / 255.0


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
