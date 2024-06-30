import string
from lark import Transformer, Tree, v_args
from lark.grammar import Terminal
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
import random

grammar_spec = r"""
s: element | style_element
element: compose | div | paragraph | button
compose: "(" "Compose" " " element " " element ")"
div: "(" "Div" " " style_element " " element ")"
paragraph: "(" "P" " " "'" text "'" ")"
text: TEXTT
TEXTT: /[^']+/
button: "(" "Button" ")" -> butt

style_element: style_pair | style_junct
style_junct: "(" "Junct" " " style_element " " style_element ")"
style_pair: style_border | style_width | style_height | style_margin_top | style_margin_left | style_margin_right | style_margin_bottom | style_background_color

style_border: "border" ":" size unit " " color
style_background_color: "background-color" ":" color
style_width: "width" ":" size unit
style_height: "height" ":" size unit
style_margin_top: "margin-top" ":" margin_value
style_margin_left: "margin-left" ":" margin_value
style_margin_right: "margin-right" ":" margin_value
style_margin_bottom: "margin-bottom" ":" margin_value
margin_value: size unit | "auto" -> auto

color: "red" -> red | "blue" -> blue | "green" -> green
number: SIGNED_NUMBER
size: number
unit: "px" -> px | "%" -> percent

%import common.SIGNED_NUMBER
%ignore /[\t\n\f\r]+/ 
"""

_SCREEN_WIDTH = 1512 // 2
_SCREEN_HEIGHT = 982 // 2


class HTMLTransformer(Transformer):
    def s(self, children):
        return children[0]

    @v_args(inline=True)
    def text(self, text):
        return text.value.strip()

    def butt(self, _):
        return "<button>Button</button>"

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

    @v_args(inline=True)
    def number(self, value):
        return float(value)

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
        num_chars = int(children[0])
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


def generate_believable_text():
    common_words = [
        "the",
        "be",
        "to",
        "of",
        "and",
        "a",
        "in",
        "that",
        "have",
        "I",
        "it",
        "for",
        "not",
        "on",
        "with",
        "he",
        "as",
        "you",
        "do",
        "at",
        "this",
        "but",
        "his",
        "by",
        "from",
        "they",
        "we",
        "say",
        "her",
        "she",
        "or",
        "an",
        "will",
        "my",
        "one",
        "all",
        "would",
        "there",
        "their",
        "what",
        "so",
        "up",
        "out",
        "if",
        "about",
        "who",
        "get",
        "which",
        "go",
        "me",
        "when",
        "make",
        "can",
        "like",
        "time",
        "no",
        "just",
        "him",
        "know",
        "take",
        "people",
        "into",
        "year",
        "your",
        "good",
        "some",
        "could",
        "them",
        "see",
        "other",
        "than",
        "then",
        "now",
        "look",
        "only",
        "come",
        "its",
        "over",
        "think",
        "also",
        "back",
        "after",
        "use",
        "two",
        "how",
        "our",
        "work",
        "first",
        "well",
        "way",
        "even",
        "new",
        "want",
        "because",
        "any",
        "these",
        "give",
        "day",
        "most",
        "us",
    ]

    sentence_starters = [
        "The",
        "A",
        "One",
        "It",
        "There",
        "We",
        "They",
        "I",
        "You",
        "He",
        "She",
        "This",
        "That",
        "These",
        "Those",
        "Some",
        "Many",
        "Few",
        "Several",
    ]

    sentence_enders = [".", ".", ".", "!", "?"]

    num_sentences = random.randint(1, 5)
    text = []

    for _ in range(num_sentences):
        sentence = [random.choice(sentence_starters)]
        sentence_length = random.randint(3, 15)

        for _ in range(sentence_length):
            word = random.choice(common_words)
            if random.random() < 0.1:
                word = word.capitalize()
            sentence.append(word)

        sentence = " ".join(sentence) + random.choice(sentence_enders)
        text.append(sentence)

    return " ".join(text)


class HTML(Environment):
    def __init__(self):
        super().__init__()
        self._grammar = Grammar(
            grammar_spec,
            start="s",
            sample_start="element",
            primitives=["paragraph", "button", "style_pair"],
            terminal_name_to_vocab={
                "SIGNED_NUMBER": (
                    "0",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    ".",
                ),
                "TEXTT": (
                    "a",
                    "b",
                    "c",
                    "d",
                    "e",
                    "f",
                    "g",
                    "h",
                    "i",
                    "j",
                    "k",
                    "l",
                    "m",
                    "n",
                    "o",
                    "p",
                    "q",
                    "r",
                    "s",
                    "t",
                    "u",
                    "v",
                    "w",
                    "x",
                    "y",
                    "z",
                    "A",
                    "B",
                    "C",
                    "D",
                    "E",
                    "F",
                    "G",
                    "H",
                    "I",
                    "J",
                    "K",
                    "L",
                    "M",
                    "N",
                    "O",
                    "P",
                    "Q",
                    "R",
                    "S",
                    "T",
                    "U",
                    "V",
                    "W",
                    "X",
                    "Y",
                    "Z",
                    "0",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    " ",
                    ".",
                    ",",
                    "!",
                    "?",
                    "-",
                    "_",
                    "(",
                    ")",
                    "[",
                    "]",
                    "{",
                    "}",
                    ":",
                    ";",
                    "/",
                    "\\",
                ),
            },
            terminal_to_custom_sampler={
                Terminal("SIGNED_NUMBER"): lambda: round(random.uniform(0, 200), 2),
                Terminal("TEXTT"): generate_believable_text,
            },
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
