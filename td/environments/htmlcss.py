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
#give priority so that text doesn't get parsed as a style (e.g. having 'vw' in text)
content: (txt | element)+
element: div | span | p | h1 | h2 | h3 | h4 | h5 | h6 | form | input | button | text_area | label | ul | li

# elements
div: "<div" " " "style=" style ">" (content)? "</div>"
span: "<span" " " "style=" style ">" (content)? "</span>"
p: "<p" " " "style=" style ">" (content)? "</p>"
h1: "<h1" " " "style=" style ">" (content)? "</h1>"
h2: "<h2" " " "style=" style ">" (content)? "</h2>"
h3: "<h3" " " "style=" style ">" (content)? "</h3>"
h4: "<h4" " " "style=" style ">" (content)? "</h4>"
h5: "<h5" " " "style=" style ">" (content)? "</h5>"
h6: "<h6" " " "style=" style ">" (content)? "</h6>"
form: "<form" " " "style=" style ">" (content)? "</form>"
text_area: "<textarea" " " "style=" style ">" (content)? "</textarea>"
label: "<label" " " "style=" style ">" (content)? "</label>"
ul: "<ul" " " "style=" style ">" (content)? "</ul>"
li: "<li" " " "style=" style ">" (content)? "</li>"
button: "<button" " " "style=" style ">" (content)? "</button>"

input: "<input" " " "type=" "\"" input_type "\"" " " "style=" style "/>"
input_type: "text" -> input_text | "password" -> input_password | "email" -> input_email | "number" -> input_number | "date" -> input_date | "checkbox" -> input_checkbox | "radio" -> input_radio | "submit" -> input_submit

# css
style: "\"" css_rule* "\""
css_rule: width_rule | height_rule | display_rule | border_radius_rule | border_rule | background_rule | flex_direction_rule | justify_content_rule | flex_wrap_rule | align_items_rule | align_content_rule | padding_top_rule | padding_bottom_rule | padding_left_rule | padding_right_rule | margin_top_rule | margin_bottom_rule | margin_left_rule | margin_right_rule | color_rule | text_align_rule

text_align_rule: "text-align:" text_align_value ";"
text_align_value: "left" -> text_align_left | "right" -> text_align_right | "center" -> text_align_center | "justify" -> text_align_justify

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

padding_top_rule: "padding-top:" number unit ";"
padding_bottom_rule: "padding-bottom:" number unit ";"
padding_left_rule: "padding-left:" number unit ";"
padding_right_rule: "padding-right:" number unit ";"

margin_value: "auto" | number unit
margin_top_rule: "margin-top:" margin_value ";"
margin_bottom_rule: "margin-bottom:" margin_value ";"
margin_left_rule: "margin-left:" margin_value ";"
margin_right_rule: "margin-right:" margin_value ";"

border_radius_rule: "border-radius:" number unit ";"
border_rule: "border:" number unit " solid " color_value ";"

background_rule: "background:" color_value ";"

color_rule: "color:" color_value ";"

# TXT rules (include unit because it gets parsed that way e.g. 1px in txt)
txt: (unit | digit | letter | symbol | whitespace)+
letter: lowercase | uppercase
lowercase: "a" -> lower_a | "b" -> lower_b | "c" -> lower_c | "d" -> lower_d | "e" -> lower_e | "f" -> lower_f | "g" -> lower_g | "h" -> lower_h | "i" -> lower_i | "j" -> lower_j | "k" -> lower_k | "l" -> lower_l | "m" -> lower_m | "n" -> lower_n | "o" -> lower_o | "p" -> lower_p | "q" -> lower_q | "r" -> lower_r | "s" -> lower_s | "t" -> lower_t | "u" -> lower_u | "v" -> lower_v | "w" -> lower_w | "x" -> lower_x | "y" -> lower_y | "z" -> lower_z
uppercase: "A" -> upper_a | "B" -> upper_b | "C" -> upper_c | "D" -> upper_d | "E" -> upper_e | "F" -> upper_f | "G" -> upper_g | "H" -> upper_h | "I" -> upper_i | "J" -> upper_j | "K" -> upper_k | "L" -> upper_l | "M" -> upper_m | "N" -> upper_n | "O" -> upper_o | "P" -> upper_p | "Q" -> upper_q | "R" -> upper_r | "S" -> upper_s | "T" -> upper_t | "U" -> upper_u | "V" -> upper_v | "W" -> upper_w | "X" -> upper_x | "Y" -> upper_y | "Z" -> upper_z
symbol: "$" -> symbol_dollar | "&" -> symbol_ampersand | "(" -> symbol_lparen | ")" -> symbol_rparen | "*" -> symbol_asterisk | "+" -> symbol_plus | "," -> symbol_comma | "-" -> symbol_minus | "." -> symbol_period | "/" -> symbol_slash | ":" -> symbol_colon | "<" -> symbol_lt | "=" -> symbol_eq | ">" -> symbol_gt | "?" -> symbol_question | "@" -> symbol_at | "[" -> symbol_lbracket | "\\" -> symbol_backslash | "]" -> symbol_rbracket | "^" -> symbol_caret | "_" -> symbol_underscore | "`" -> symbol_backtick | "{" -> symbol_lbrace | "|" -> symbol_pipe | "}" -> symbol_rbrace | "~" -> symbol_tilde | "!" -> symbol_exclamation | ";" -> symbol_semicolon | "©" -> symbol_copyright
whitespace: " " -> space | "\t" -> tab | "\n" -> newline | "\r" -> carriage_return

# values
digit: "0" -> digit_0 | "1" -> digit_1 | "2" -> digit_2 | "3" -> digit_3 | "4" -> digit_4 | "5" -> digit_5 | "6" -> digit_6 | "7" -> digit_7 | "8" -> digit_8 | "9" -> digit_9
number: digit+ (decimal_part)?
decimal_part: "." digit+
unit: "px" -> px | "em" -> em | "rem" -> rem | "vw" -> vw | "vh" -> vh | "%" -> percent
color_value: "#" color_digit color_digit color_digit color_digit color_digit color_digit
color_digit: digit | ("a" | "A") -> color_digit_a | ("b" | "B") -> color_digit_b | ("c" | "C") -> color_digit_c | ("d" | "D") -> color_digit_d | ("e" | "E") -> color_digit_e | ("f" | "F") -> color_digit_f

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
    
    def text_area(self, items):
        style = items[0]
        content = items[1] if len(items) > 1 else ""
        return f'<textarea style="{style}">{content}</textarea>'
    
    def label(self, items):
        style = items[0]
        content = items[1] if len(items) > 1 else ""
        return f'<label style="{style}">{content}</label>'
    
    def ul(self, items):
        style = items[0]
        content = "".join(items[1:])
        return f'<ul style="{style}">{content}</ul>'
    
    def li(self, items):
        style = items[0]
        content = items[1] if len(items) > 1 else ""
        return f'<li style="{style}">{content}</li>'

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
    
    def input_submit(self, children):
        return "submit"

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
    
    def padding_top_rule(self, items):
        return f"padding-top:{items[0]}{items[1]};"

    def padding_bottom_rule(self, items):
        return f"padding-bottom:{items[0]}{items[1]};"

    def padding_left_rule(self, items):
        return f"padding-left:{items[0]}{items[1]};"

    def padding_right_rule(self, items):
        return f"padding-right:{items[0]}{items[1]};"
    
    def margin_value(self, items):
        if len(items) == 0:
            return "auto"
        return f"{items[0]}{items[1]}"
    
    def margin_top_rule(self, items):
        return f"margin-top:{items[0]};"
    
    def margin_bottom_rule(self, items):
        return f"margin-bottom:{items[0]};"
    
    def margin_left_rule(self, items):
        return f"margin-left:{items[0]};"
    
    def margin_right_rule(self, items):
        return f"margin-right:{items[0]};"
    
    
    def color_rule(self, items):
        return f"color:{items[0]};"
    
    def text_align_rule(self, items):
        return f"text-align:{items[0]};"
    
    # updated values
    def txt(self, items):
        return "".join(items)

    def letter(self, items):
        return items[0]

    def lowercase(self, items):
        return items[0]

    def uppercase(self, items):
        return items[0]

    def symbol(self, items):
        return items[0]

    def whitespace(self, items):
        return items[0]

    def digit(self, items):
        return items[0]

    def decimal_part(self, items):
        return f".{''.join(items)}"

    def number(self, items):
        # clip the number to 3 digits (in front of the decimal point)
        num_s = "".join(items)
        num = float(num_s) % 1_000
        if num.is_integer():
            return str(int(num))
        return str(num)

        



    def color_value(self, items):
        return "#" + "".join(items)

    def color_digit(self, items):
        return items[0]
    
    # Lowercase letters
    def lower_a(self, _): return "a"
    def lower_b(self, _): return "b"
    def lower_c(self, _): return "c"
    def lower_d(self, _): return "d"
    def lower_e(self, _): return "e"
    def lower_f(self, _): return "f"
    def lower_g(self, _): return "g"
    def lower_h(self, _): return "h"
    def lower_i(self, _): return "i"
    def lower_j(self, _): return "j"
    def lower_k(self, _): return "k"
    def lower_l(self, _): return "l"
    def lower_m(self, _): return "m"
    def lower_n(self, _): return "n"
    def lower_o(self, _): return "o"
    def lower_p(self, _): return "p"
    def lower_q(self, _): return "q"
    def lower_r(self, _): return "r"
    def lower_s(self, _): return "s"
    def lower_t(self, _): return "t"
    def lower_u(self, _): return "u"
    def lower_v(self, _): return "v"
    def lower_w(self, _): return "w"
    def lower_x(self, _): return "x"
    def lower_y(self, _): return "y"
    def lower_z(self, _): return "z"

    # Uppercase letters
    def upper_a(self, _): return "A"
    def upper_b(self, _): return "B"
    def upper_c(self, _): return "C"
    def upper_d(self, _): return "D"
    def upper_e(self, _): return "E"
    def upper_f(self, _): return "F"
    def upper_g(self, _): return "G"
    def upper_h(self, _): return "H"
    def upper_i(self, _): return "I"
    def upper_j(self, _): return "J"
    def upper_k(self, _): return "K"
    def upper_l(self, _): return "L"
    def upper_m(self, _): return "M"
    def upper_n(self, _): return "N"
    def upper_o(self, _): return "O"
    def upper_p(self, _): return "P"
    def upper_q(self, _): return "Q"
    def upper_r(self, _): return "R"
    def upper_s(self, _): return "S"
    def upper_t(self, _): return "T"
    def upper_u(self, _): return "U"
    def upper_v(self, _): return "V"
    def upper_w(self, _): return "W"
    def upper_x(self, _): return "X"
    def upper_y(self, _): return "Y"
    def upper_z(self, _): return "Z"

    # symbols
    def symbol_dollar(self, _): return "$"
    def symbol_percent(self, _): return "%"
    def symbol_ampersand(self, _): return "&"
    def symbol_lparen(self, _): return "("
    def symbol_rparen(self, _): return ")"
    def symbol_asterisk(self, _): return "*"
    def symbol_plus(self, _): return "+"
    def symbol_comma(self, _): return ","
    def symbol_minus(self, _): return "-"
    def symbol_period(self, _): return "."
    def symbol_slash(self, _): return "/"
    def symbol_colon(self, _): return ":"
    def symbol_lt(self, _): return "<"
    def symbol_eq(self, _): return "="
    def symbol_gt(self, _): return ">"
    def symbol_question(self, _): return "?"
    def symbol_at(self, _): return "@"
    def symbol_lbracket(self, _): return "["
    def symbol_backslash(self, _): return "\\"
    def symbol_rbracket(self, _): return "]"
    def symbol_caret(self, _): return "^"
    def symbol_underscore(self, _): return "_"
    def symbol_backtick(self, _): return "`"
    def symbol_lbrace(self, _): return "{"
    def symbol_pipe(self, _): return "|"
    def symbol_rbrace(self, _): return "}"
    def symbol_tilde(self, _): return "~"
    def symbol_exclamation(self, _): return "!"
    def symbol_semicolon(self, _): return ";"
    def symbol_copyright(self, _): return "©"

    # whitespace
    def space(self, _):
        return " "

    def tab(self, _):
        return "\t"

    def newline(self, _):
        return "\n"

    def carriage_return(self, _):
        return "\r"

    # values
    
    def color_digit_a(self, _):
        return "a"
    
    def color_digit_b(self, _):
        return "b"
    
    def color_digit_c(self, _):
        return "c"
    
    def color_digit_d(self, _):
        return "d"
    
    def color_digit_e(self, _):
        return "e"
    
    def color_digit_f(self, _):
        return "f"
    
    def digit_0(self, _):
        return "0"
    
    def digit_1(self, _):
        return "1"
    
    def digit_2(self, _):
        return "2"
    
    def digit_3(self, _):
        return "3"
    
    def digit_4(self, _):
        return "4"
    
    def digit_5(self, _):
        return "5"
    
    def digit_6(self, _):
        return "6"
    
    def digit_7(self, _):
        return "7"
    
    def digit_8(self, _):
        return "8"
    
    def digit_9(self, _):
        return "9"

    def text_align_left(self, _):
        return "left"
    
    def text_align_right(self, _):
        return "right"
    
    def text_align_center(self, _):
        return "center"
    
    def text_align_justify(self, _):
        return "justify"

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
    
    def signed_number(self, children):
        number_str = ''.join(children)
        number = float(number_str)
        if number.is_integer():
            return str(int(number))
        else:
            return f'{number:.10f}'.rstrip('0').rstrip('.')


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
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        self._driver = webdriver.Chrome(options=chrome_options)
        self._driver.get("about:blank")
        self._driver.execute_script("document.body.style = 'margin: 0; padding: 0;'")
    def compile(self, expression: Tree):
        content = self._expression_to_html.transform(expression)
        try:
            self._driver.execute_script(f"document.body.innerHTML = '{content}'")
        except Exception as e:
            print(f"error compiling expression: {expression}")
            print(f"errored content: {content}")
            raise e
        
        # Define maximum allowable dimensions
        MAX_WIDTH = 1000
        MAX_HEIGHT = 2000

        total_width = self._driver.execute_script("return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
        total_height = self._driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")

        # Constrain the dimensions to maximum values
        total_width = min(total_width, MAX_WIDTH)
        total_height = min(total_height, MAX_HEIGHT)

        self._driver.set_window_size(total_width, total_height)
        
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
            sample_start="element",
            primitives=["element", "txt", "css_rule"],
            sampling_weights={
                "__number_plus_3": [0.8, 0.2], # 20% chance of expanding number
                # "__txt_plus_3": [ 0.05, 0.05, 0.05, 0.05, 0.2, 0.2, 0.2, 0.2], # the last 4 (which continue the sequence) have a higher chance of being chosen
                "__txt_plus_2": [0.1, 0.1, 0.1, 0, 0, 1, 1, 1, 0, 0]
            }
            # terminal_name_to_vocab={
            #     "SIGNED_NUMBER": string.digits + ".",
            #     "COLOR_VALUE": string.hexdigits + "#",
            #     "TXT": string.digits + string.ascii_letters + string.whitespace + r"""$%&()*+,-./:<=>?@[\]^_`{|}~""",
            # },
            # terminal_to_custom_sampler={
            #     Terminal("TXT"): generate_believable_text,
            #     Terminal("COLOR_VALUE"): lambda: "#"
            #     + "".join(random.choice(string.hexdigits) for _ in range(6)),
            #     Terminal("SIGNED_NUMBER"): lambda: round(random.uniform(0, 10), 2),
            # },
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

import re

def clean_css_whitespace(css):
    css = re.sub(r'\s*([{};:,])\s*', r'\1', css)
    css = re.sub(r'\s+', ' ', css)
    return css.strip()

def clean_html_whitespace(html_string):
    def clean_tag(match):
        tag = match.group(0)
        if 'style="' in tag:
            style_pattern = r'(style=")([^"]*)"(\s*)'
            tag = re.sub(style_pattern, lambda m: m.group(1) + clean_css_whitespace(m.group(2)) + '"', tag)
        return re.sub(r'\s+', ' ', tag).strip()

    preserve_space_tags = ['pre', 'code', 'textarea']
    
    for tag in preserve_space_tags:
        if tag == 'textarea':
            pattern = r'(<textarea[^>]*>)'
            html_string = re.sub(pattern, lambda m: re.sub(r'(style=")([^"]*)"',
                                                         lambda n: n.group(1) + clean_css_whitespace(n.group(2)) + '"',
                                                         m.group(1)), html_string, flags=re.DOTALL)
        
        pattern = r'(<{0}[^>]*>)(.*?)(</{0}>)'.format(tag)
        html_string = re.sub(pattern, 
                             lambda m: m.group(1).replace(' ', '\0') + m.group(2) + m.group(3).replace(' ', '\0'), 
                             html_string, 
                             flags=re.DOTALL)

    html_string = re.sub(r'<[^>]+>', clean_tag, html_string)
    html_string = re.sub(r'>\s+<', '><', html_string)
    html_string = re.sub(r' +', ' ', html_string)
    html_string = html_string.replace('\0', ' ')
    html_string = re.sub(r' +>', '>', html_string)
    
    return html_string.strip()
