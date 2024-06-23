from lark import Transformer, Tree, v_args
from td.grammar import Compiler, Grammar
from td.environments.environment import Environment
from td.environments.goal_checker import GaussianImageGoalChecker
import imgkit
from io import BytesIO
from PIL import Image as PILImage
import numpy as np

from PIL import Image
import numpy as np

grammar_spec = r"""

    compose: "(" "Compose" element element ")"
    element: paragraph | div | compose
    paragraph: "(" "P" "'" text "'" ")"
    // (Div x y style element)
    div: "(" "Div" style element ")"
    //TEXT: /[a-zA-Z0-9\s]+/
    text: number -> loremipsum

    style: "(" "Style" style_element ")"
    style_junct: "(" "Junct" style_element style_element ")"
    style_element: style_pair | style_junct
    style_border: "border" ":" size unit color
    style_width: "width" ":" size unit
    style_height: "height" ":" size unit
    margin_value: size unit | "auto" -> auto
    style_margin_top: "margin-top" ":" margin_value
    style_margin_left: "margin-left" ":" margin_value
    style_margin_right: "margin-right" ":" margin_value
    style_margin_bottom: "margin-bottom" ":" margin_value
    style_pair: style_border | style_width | style_height | style_margin_top | style_margin_left | style_margin_right | style_margin_bottom

    color: "red" -> red | "blue" -> blue | "green" -> green
    number: "0" -> zero | "1" -> one | "2" -> two | "3" -> three | "4" -> four | "5" -> five | "6" -> six | "7" -> seven | "8" -> eight | "9" -> nine | "A" -> ten | "B" -> eleven | "C" -> twelve | "D" -> thirteen | "E" -> fourteen | "F" -> fifteen | "12" -> twelve | "24" -> twentyfour | "36" -> thirtysix | "50" -> fifty | "100" -> hundred
    size: number
    unit: "px" -> px | "%" -> percent

    %ignore /[\t \n\f\r]+/  // Ignore whitespace
"""
# 1512, 982
_SCREEN_WIDTH = 1512 // 2
_SCREEN_HEIGHT = 982 // 2


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

    def style_margin_top(self, children):
        return f"margin-top: {children[0]}"

    def style_margin_left(self, children):
        return f"margin-left: {children[0]}"

    def style_margin_right(self, children):
        return f"margin-right: {children[0]}"

    def style_margin_bottom(self, children):
        return f"margin-bottom: {children[0]}"

    def margin_value(self, children):
        if len(children) == 1:
            return children[0]
        else:
            return f"{children[0]}{children[1]}"

    def auto(self, _):
        return "auto"

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

    def zero(self, _):
        return 0

    def one(self, _):
        return 1

    def two(self, _):
        return 2

    def three(self, _):
        return 3

    def four(self, _):
        return 4

    def five(self, _):
        return 5

    def six(self, _):
        return 6

    def seven(self, _):
        return 7

    def eight(self, _):
        return 8

    def nine(self, _):
        return 9

    def ten(self, _):
        return 10

    def eleven(self, _):
        return 11

    def twelve(self, _):
        return 12

    def thirteen(self, _):
        return 13

    def fourteen(self, _):
        return 14

    def fifteen(self, _):
        return 15

    def twentyfour(self, _):
        return 24

    def thirtysix(self, _):
        return 36

    def fifty(self, _):
        return 50

    def hundred(self, _):
        return 100

    def size(self, children):
        return children[0]

    def red(self, _):
        return "red"

    def blue(self, _):
        return "blue"

    def green(self, _):
        return "green"

    def px(self, _):
        return "px"

    def loremipsum(self, children):
        num_chars = children[0]
        phrase = "Lorem Ipsum"
        repeated_text = (phrase * (num_chars // len(phrase) + 1))[:num_chars]
        return repeated_text

    def percent(self, _):
        return "%"


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

    # def compile(self, expression: Tree):
    #     content = self._expression_to_html.transform(expression)
    #     html = f"<html><body>{content}</body></html>"
    #     img_raw = imgkit.from_string(
    #         html,
    #         False,
    #         options={
    #             "format": "png",
    #             "quiet": "",
    #             # "crop-w": _SCREEN_WIDTH,
    #             # "crop-h": _SCREEN_HEIGHT,
    #         },
    #     )
    #     stream = BytesIO(img_raw)
    #     image = PILImage.open(stream)
    #     if image.mode != "RGB":
    #         image = image.convert("RGB")
    #     desired_width = _SCREEN_WIDTH
    #     desired_height = _SCREEN_HEIGHT
    #     image = image.resize((desired_width, desired_height), PILImage.LANCZOS)
    #     image_array = np.array(image)
    #     image.close()
    #     stream.close()
    #     # print(image_array.shape)
    #     # assert image_array.shape == (_SCREEN_HEIGHT, _SCREEN_WIDTH, 3)
    #     # print("compile array shape")
    #     return image_array / 255.0
    #     # return np.load("/Users/nathanvogt/tree-diffusion/html.npy")

    def compile(self, expression: Tree):
        content = self._expression_to_html.transform(expression)
        html = f"<html><body>{content}</body></html>"
        # print(html)
        img_raw = imgkit.from_string(
            html,
            False,
            options={
                "format": "png",
                "height": _SCREEN_HEIGHT,
                "width": _SCREEN_WIDTH,
                "quiet": "",
            },
        )
        stream = BytesIO(img_raw)
        image = PILImage.open(stream)
        if image.mode != "RGB":
            image = image.convert("RGB")

        desired_width = _SCREEN_WIDTH
        desired_height = _SCREEN_HEIGHT
        img_ratio = image.width / image.height
        target_ratio = desired_width / desired_height

        if target_ratio > img_ratio:
            new_width = int(desired_height * img_ratio)
            image = image.resize((new_width, desired_height), PILImage.LANCZOS)
            new_image = PILImage.new(
                "RGB", (desired_width, desired_height), (255, 255, 255)
            )
            padding = (desired_width - new_width) // 2
            new_image.paste(image, (padding, 0))
        elif target_ratio < img_ratio:
            new_height = int(desired_width / img_ratio)
            image = image.resize((desired_width, new_height), PILImage.LANCZOS)
            new_image = PILImage.new(
                "RGB", (desired_width, desired_height), (255, 255, 255)
            )
            padding = (desired_height - new_height) // 2
            new_image.paste(image, (0, padding))
        else:
            new_image = image.resize((desired_width, desired_height), PILImage.LANCZOS)

        image_array = np.array(new_image)
        image.close()
        stream.close()
        return image_array / 255.0


class HTML(Environment):
    def __init__(self):
        super().__init__()
        self._grammar = Grammar(
            grammar_spec,
            start="element",
            primitives=["paragraph", "div", "style_element"],
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
