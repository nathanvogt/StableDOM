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
start: content | style
content: element*
element: div | span | p | ul | li | h1 | h2 | h3 | h4 | h5 | h6 | form | input | button

# elements
div: "<div" "style=" style ">" (content | TXT)? "</div>"
span: "<span" "style=" style ">" (content | TXT)? "</span>"
p: "<p" "style=" style ">" (content | TXT)? "</p>"
ul: "<ul" "style=" style ">" li* "</ul>"
li: "<li" "style=" style ">" (content | TXT)? "</li>"
h1: "<h1" "style=" style ">" (content | TXT)? "</h1>"
h2: "<h2" "style=" style ">" (content | TXT)? "</h2>"
h3: "<h3" "style=" style ">" (content | TXT)? "</h3>"
h4: "<h4" "style=" style ">" (content | TXT)? "</h4>"
h5: "<h5" "style=" style ">" (content | TXT)? "</h5>"
h6: "<h6" "style=" style ">" (content | TXT)? "</h6>"
form: "<form" "style=" style ">" (content | TXT)? "</form>"

input: "<input" "type=" "\"" input_type "\"" "style=" style "/>"
input_type: "text" -> input_text | "password" -> input_password | "email" -> input_email | "number" -> input_number | "date" -> input_date | "checkbox" -> input_checkbox | "radio" -> input_radio

button: "<button" "style=" style ">" (content | TXT)? "</button>"

# css
style: "\"" css_rule* "\""

css_rule: width_rule | height_rule | display_rule | border_radius_rule | border_rule | background_rule | flex_direction_rule | justify_content_rule | flex_wrap_rule | align_items_rule | align_content_rule

width_rule: "width:" number unit ";"
height_rule: "height:" number unit ";"

display_rule: "display:" display_value ";"
display_value: "block" -> display_block | "inline" -> display_inline | "inline-block" -> display_inline_block | "none" -> display_none | "flex" -> display_flex | "grid" -> display_grid

flex_direction_rule: "flex-direction:" flex_direction_value ";"
flex_direction_value: "row" -> row | "row-reverse" -> row_reverse | "column" -> column | "column-reverse" -> column_reverse
justify_content_rule: "justify-content:" justify_content_value ";"
justify_content_value: "flex-start" -> flex_start | "flex-end" -> flex_end | "center" -> center | "space-between" -> space_between | "space-around" -> space_around | "space-evenly" -> space_evenly
flex_wrap_rule: "flex-wrap:" flex_wrap_value ";"
flex_wrap_value: "nowrap" -> nowrap | "wrap" -> wrap | "wrap-reverse" -> wrap_reverse
align_items_rule: "align-items:" align_items_value ";"
align_items_value: "stretch" -> stretch | "flex-start" -> flex_start | "flex-end" -> flex_end | "center" -> center | "baseline" -> baseline
align_content_rule: "align-content:" align_content_value ";"
align_content_value: "stretch" -> stretch | "flex-start" -> flex_start | "flex-end" -> flex_end | "center" -> center | "space-between" -> space_between | "space-around" -> space_around


border_radius_rule: "border-radius:" number unit ";"
border_rule: "border:" number unit "solid" COLOR ";"

background_rule: "background:" COLOR ";"

# values
number: SIGNED_NUMBER
unit: "px" -> px | "em" -> em | "rem" -> rem | "vw" -> vw | "vh" -> vh | "%" -> percent
TXT: /[^<>]+/
COLOR: /\#[0-9a-fA-F]{6}/

%import common.SIGNED_NUMBER
%import common.WS
%ignore WS
"""

_SCREEN_WIDTH = 1512 // 2
_SCREEN_HEIGHT = 982 // 2


class HTMLCSSTransformer(Transformer):
    def start(self, items):
        return "".join(items)

    def content(self, items):
        return "".join(items)

    def element(self, items):
        return "".join(items)

    def div(self, items):
        style = items[0]
        content = items[1] if len(items) > 1 else ""
        return f'<div style="{style}">{content}</div>'

    def span(self, items):
        style = items[0]
        content = items[1] if len(items) > 1 else ""
        return f'<span style="{style}">{content}</span>'

    def p(self, items):
        style = items[0]
        content = items[1] if len(items) > 1 else ""
        return f'<p style="{style}">{content}</p>'

    def a(self, items):
        href = items[0]
        style = items[1]
        content = items[2] if len(items) > 2 else ""
        return f'<a href={href} style="{style}">{content}</a>'

    def ul(self, items):
        style = items[0]
        content = "".join(items[1:])
        return f'<ul style="{style}">{content}</ul>'

    def li(self, items):
        style = items[0]
        content = items[1] if len(items) > 1 else ""
        return f'<li style="{style}">{content}</li>'

    def h1(self, items):
        style = items[0]
        content = items[1] if len(items) > 1 else ""
        return f'<h1 style="{style}">{content}</h1>'

    def h2(self, items):
        style = items[0]
        content = items[1] if len(items) > 1 else ""
        return f'<h2 style="{style}">{content}</h2>'

    def h3(self, items):
        style = items[0]
        content = items[1] if len(items) > 1 else ""
        return f'<h3 style="{style}">{content}</h3>'

    def h4(self, items):
        style = items[0]
        content = items[1] if len(items) > 1 else ""
        return f'<h4 style="{style}">{content}</h4>'

    def h5(self, items):
        style = items[0]
        content = items[1] if len(items) > 1 else ""
        return f'<h5 style="{style}">{content}</h5>'

    def h6(self, items):
        style = items[0]
        content = items[1] if len(items) > 1 else ""
        return f'<h6 style="{style}">{content}</h6>'

    def form(self, items):
        style = items[0]
        content = "".join(items[1:])
        return f'<form style="{style}">{content}</form>'

    def input(self, items):
        type_attr = items[0]
        style = items[1]
        return f'<input type={type_attr} style="{style}"/>'

    def input_text(self, children):
        return "text"

    def input_password(self, children):
        return "password"

    def input_email(self, children):
        return "email"

    def input_number(self, children):
        return "number"

    def input_date(self, children):
        return "date"

    def input_checkbox(self, children):
        return "checkbox"

    def input_radio(self, children):
        return "radio"

    def button(self, items):
        style = items[0]
        content = items[1] if len(items) > 1 else ""
        return f'<button style="{style}">{content}</button>'

    def style(self, items):
        return "".join(items)

    def css_rule(self, items):
        return "".join(items)

    def width_rule(self, items):
        return f"width:{items[0]}{items[1]};"

    def height_rule(self, items):
        return f"height:{items[0]}{items[1]};"

    def display_rule(self, items):
        return f"display:{items[0]};"

    def display_value(self, children):
        return children[0]

    def display_block(self, children):
        return "block"

    def display_inline(self, children):
        return "inline"

    def display_inline_block(self, children):
        return "inline-block"

    def display_none(self, children):
        return "none"

    def display_flex(self, children):
        return "flex"

    def display_grid(self, children):
        return "grid"

    def border_radius_rule(self, items):
        return f"border-radius:{items[0]}{items[1]};"

    def border_rule(self, items):
        return f"border:{items[0]}{items[1]} solid {items[2]};"

    def background_rule(self, items):
        return f"background:{items[0]};"

    # flex properties
    def row(self, _):
        return "row"

    def row_reverse(self, _):
        return "row-reverse"

    def column(self, _):
        return "column"

    def column_reverse(self, _):
        return "column-reverse"

    def nowrap(self, _):
        return "nowrap"

    def wrap(self, _):
        return "wrap"

    def wrap_reverse(self, _):
        return "wrap-reverse"

    def flex_start(self, _):
        return "flex-start"

    def flex_end(self, _):
        return "flex-end"

    def center(self, _):
        return "center"

    def baseline(self, _):
        return "baseline"

    def stretch(self, _):
        return "stretch"

    def space_between(self, _):
        return "space-between"

    def space_around(self, _):
        return "space-around"

    def space_evenly(self, _):
        return "space-evenly"

    # Methods for flex rules
    def flex_direction_rule(self, items):
        return f"flex-direction: {items[0]};"

    def flex_wrap_rule(self, items):
        return f"flex-wrap: {items[0]};"

    def justify_content_rule(self, items):
        return f"justify-content: {items[0]};"

    def align_items_rule(self, items):
        return f"align-items: {items[0]};"

    def align_content_rule(self, items):
        return f"align-content: {items[0]};"

    def number(self, chilren):
        return chilren[0]

    def unit(self, children):
        return children[0]

    def px(self, children):
        return "px"

    def em(self, children):
        return "em"

    def rem(self, children):
        return "rem"

    def vw(self, children):
        return "vw"

    def vh(self, children):
        return "vh"

    def percent(self, children):
        return "%"

    def ESCAPED_STRING(self, token):
        return token.value

    def SIGNED_NUMBER(self, token):
        return token.value

    def COLOR(self, token):
        return token.value

    def TXT(self, token):
        return token.value


class HTMLCSSCompiler(Compiler):
    def __init__(self):
        super().__init__()
        print("Initializing HTMLCompiler")
        self._expression_to_html = HTMLCSSTransformer()
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
        content = self._expression_to_html.transform(expression)
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

    sentence_enders = [".", "!", "?", "..."]

    adjectives = [
        "quick",
        "lazy",
        "beautiful",
        "loud",
        "mysterious",
        "strange",
        "bright",
        "dark",
        "light",
    ]

    num_sentences = random.randint(1, 3)
    text = []

    for _ in range(num_sentences):
        sentence = [random.choice(sentence_starters)]
        sentence_length = random.randint(5, 12)

        for _ in range(sentence_length):
            word = random.choice(common_words)
            if random.random() < 0.2:  # Increased chance for capitalization
                word = word.capitalize()
            if random.random() < 0.15:  # Chance to insert an adjective
                word = random.choice(adjectives) + " " + word
            sentence.append(word)

        sentence = " ".join(sentence) + random.choice(sentence_enders)
        if (
            random.random() < 0.3
        ):  # Chance to add a connector for more complex sentences
            connector = random.choice(
                ["However,", "Moreover,", "Nevertheless,", "Thus,", "Meanwhile,"]
            )
            next_sentence = generate_short_sentence(
                common_words, sentence_starters, adjectives
            )
            sentence += " " + connector + " " + next_sentence

        text.append(sentence)

    return " ".join(text)


def generate_short_sentence(common_words, sentence_starters, adjectives):
    sentence = [random.choice(sentence_starters)]
    sentence_length = random.randint(3, 7)
    for _ in range(sentence_length):
        word = random.choice(common_words)
        if random.random() < 0.1:  # Consistency in style choices
            word = word.capitalize()
        if random.random() < 0.1:
            word = random.choice(adjectives) + " " + word
        sentence.append(word)
    return " ".join(sentence) + random.choice([".", "!", "?", "..."])


class HTMLCSS(Environment):
    def __init__(self):
        super().__init__()
        self._grammar = Grammar(
            grammar_spec,
            start="start",
            sample_start="content",
            primitives=["element", "css_rule"],
            terminal_name_to_vocab={
                "WORD": string.ascii_letters + "-",
                "NUMBER": string.digits + ".",
                "COLOR": string.hexdigits + "#",
                "TXT": string.printable,
                "ESCAPED_STRING": string.printable,
            },
            terminal_to_custom_sampler={
                Terminal("TXT"): generate_believable_text,
                Terminal("COLOR"): lambda: "#"
                + "".join(random.choice(string.hexdigits) for _ in range(6)),
                Terminal("SIGNED_NUMBER"): lambda: round(random.uniform(0, 10), 2),
            },
        )
        self._compiler = HTMLCSSCompiler()
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
        return "htmlcss"

    def goal_reached(self, compiledA, compiledB):
        return self._goal_checker.goal_reached(compiledA, compiledB)
