from lark import Transformer, Tree, v_args
from td.grammar import Compiler, Grammar
from td.environments.environment import Environment
from td.environments.goal_checker import GaussianImageGoalChecker
import numpy as np
from PIL import Image as PILImage
from io import BytesIO
import imgkit
from lark import Tree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import io

grammar_spec = r"""
s: element | style_element
element: div | paragraph | compose
compose: "(" "Compose" " " element " " element ")"
div: "(" "Div" " " style_element " " element ")"
paragraph: "(" "P" " " "'" text "'" ")"
text: number -> loremipsum

style_element: style_pair | style_junct
style_junct: "(" "Junct" " " style_element " " style_element ")"
style_pair: style_border | style_width | style_height | style_margin_top | style_margin_left | style_margin_right | style_margin_bottom | style_background_color
style_border: "border" ":" size unit " " color
style_background_color: "background-color" ":" color
style_width: "width" ":" size unit
style_height: "height" ":" size unit
margin_value: size unit | "auto" -> auto
style_margin_top: "margin-top" ":" margin_value
style_margin_left: "margin-left" ":" margin_value
style_margin_right: "margin-right" ":" margin_value
style_margin_bottom: "margin-bottom" ":" margin_value

color: "red" -> red | "blue" -> blue | "green" -> green
number: "0" -> zero | "1" -> one | "2" -> two | "3" -> three | "4" -> four | "5" -> five | "6" -> six | "7" -> seven | "8" -> eight | "9" -> nine | "10" -> ten | "11" -> eleven | "12" -> twelve | "13" -> thirteen | "14" -> fourteen | "15" -> fifteen | "24" -> twentyfour | "36" -> thirtysix | "50" -> fifty | "100" -> hundred
size: number
unit: "px" -> px | "%" -> percent

%ignore /[\t\n\f\r]+/ 
"""

_SCREEN_WIDTH = 1512 // 2
_SCREEN_HEIGHT = 982 // 2


class HTMLTransformer(Transformer):
    def s(self, children):
        return children[0]

    @v_args(inline=True)
    def text(self, text):
        return text.strip()

    def style_border(self, children):
        (size, unit, color) = children
        return f"border: {size}{unit} solid {color}"

    def style_background_color(self, children):
        return f"background-color: {children[0]}"

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
        (style, elements) = children
        return f"<div style='{style}'>" + "".join(elements) + "</div>"

    def paragraph(self, children):
        text = children[0]
        return f"<p>{text}</p>"

    def element(self, children):
        return children[0]

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
        return "rgba(255, 0, 0, 0.5)"

    def blue(self, _):
        return "rgba(0, 0, 255, 0.5)"

    def green(self, _):
        return "rgba(0, 255, 0, 0.5)"

    def px(self, _):
        return "px"

    def loremipsum(self, children):
        num_chars = children[0]
        phrase = "Lorem Ipsum"
        repeated_text = (phrase * (num_chars // len(phrase) + 1))[:num_chars]
        return repeated_text

    def percent(self, _):
        return "%"


class HTMLCompiler(Compiler):
    def __init__(self):
        super().__init__()
        print("Initializing HTMLCompiler")
        self._expression_to_html = HTMLTransformer()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument(f"--window-size={_SCREEN_WIDTH},{_SCREEN_HEIGHT}")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        self._driver = webdriver.Chrome(options=chrome_options)
        self._driver.get("about:blank")

    def compile(self, expression: Tree):
        content = self._expression_to_html.transform(expression).replace("'", "\\'")
        self._driver.execute_script(f"document.body.innerHTML = '{content}'")
        png = self._driver.get_screenshot_as_png()

        image = Image.open(io.BytesIO(png))
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
        return image_array / 255.0

    def __del__(self):
        self._driver.quit()


class HTML(Environment):
    def __init__(self):
        super().__init__()
        self._grammar = Grammar(
            grammar_spec,
            start="s",
            sample_start="element",
            primitives=["paragraph", "style_pair"],
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
