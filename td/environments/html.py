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
start: html_document
html_document: "<html>" head body "</html>"
head: "<head>" "</head>"
body: "<body>" content "</body>"
content: element*
element: div | span | p | a | ul | li | h1 | h2 | h3 | h4 | h5 | h6 | table | form | input | button

# elements
div: "<div>" (content | TEXT)? "</div>"
span: "<span>" (content | TEXT)? "</span>"
p: "<p>" (content | TEXT)? "</p>"
a: "<a>" (content | TEXT)? "</a>"
ul: "<ul>" (li)* "</ul>"
li: "<li>" (content | TEXT)? "</li>"
h1: "<h1>" (content | TEXT)? "</h1>"
h2: "<h2>" (content | TEXT)? "</h2>"
h3: "<h3>" (content | TEXT)? "</h3>"
h4: "<h4>" (content | TEXT)? "</h4>"
h5: "<h5>" (content | TEXT)? "</h5>"
h6: "<h6>" (content | TEXT)? "</h6>"
table: "<table>" (tr)* "</table>"
tr: "<tr>" (td)* "</tr>"
td: "<td>" (content | TEXT)? "</td>"
form: "<form>" (content | TEXT)? "</form>"
input: "<input>" (content | TEXT)? "</input>"
button: "<button>" (content | TEXT)? "</button>"

# css
style: "idk"

display_rule: "display:" display_value ";"
display_value: "block" | "inline" | "inline-block"

TEXT: /[^<>]+/

%import common.WS
%ignore WS
"""

_SCREEN_WIDTH = 1512 // 2
_SCREEN_HEIGHT = 982 // 2


class HTMLCSSTransformer(Transformer):
    pass


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

    num_sentences = random.randint(1, 3)
    text = []

    for _ in range(num_sentences):
        sentence = [random.choice(sentence_starters)]
        sentence_length = random.randint(1, 8)

        for _ in range(sentence_length):
            word = random.choice(common_words)
            if random.random() < 0.1:
                word = word.capitalize()
            sentence.append(word)

        sentence = " ".join(sentence) + random.choice(sentence_enders)
        text.append(sentence)

    return " ".join(text)


class HTMLCSS(Environment):
    def __init__(self):
        super().__init__()
        self._grammar = Grammar(
            grammar_spec,
            start="start",
            sample_start="html_document",
            primitives=["element", "css_rule"],
            terminal_name_to_vocab={
                "WORD": string.ascii_letters + "-",
                "NUMBER": string.digits + ".",
                "COLOR": string.hexdigits + "#",
                "TEXT": string.printable,
                "ESCAPED_STRING": string.printable,
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
        return "html"

    def goal_reached(self, compiledA, compiledB):
        return self._goal_checker.goal_reached(compiledA, compiledB)
