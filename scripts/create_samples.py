import random   
from td.environments.htmlcss import HTMLCSS
import os
from openai import OpenAI

openai_client = OpenAI(
    api_key=''
)

samples_dir = "/Users/nathanvogt/tree-diffusion/samples"
bad_samples_dir = "/Users/nathanvogt/tree-diffusion/bad_samples"

def get_random_theme():
    themes = [
        "Minimalist Photography Portfolio",
        "Retro Vinyl Record Store",
        "Modern Tech Startup Landing Page",
        "Cozy Bookstore Blog",
        "Personal Fitness Trainer",
        "Eco-Friendly Gardening Tips",
        "Artisan Coffee Shop",
        "Local Farmers Market",
        "Indie Game Developer Hub",
        "Travel Photographer Journal",
        "Wellness and Meditation Center",
        "DIY Home Renovation Tips",
        "Craft Beer Brewery",
        "Urban Streetwear Fashion",
        "Vintage Car Club",
        "Wildlife Conservation Non-Profit",
        "Local Bakery and Confectionery",
        "Freelance Graphic Designer Portfolio",
        "Organic Skincare Products",
        "Adventure Sports Coaching"
    ]
    return random.choice(themes)

def get_prompt(theme):
    return f"""
Create a basic but realistic website using strictly the following specified grammar. Use the website theme: {theme}. You can only use tags that are in the specification. You must use inline styles and can only use the style rules present in the specification. Make sure to also only use style values that are permitted by the specification. Even if an element has no style added, it must have an empty 'style=""' on it. Don't include any '<html>' '<body>' '<head>' or anything like that. Only use what is available in the specification. Assume that this will be accounted for. Note that the specification does not allow for general style attributes like 'padding' or 'margin'. It only has the specific sided-variants like 'margin-top' and 'padding-bottom'. Also, note that hex shorthand can not be used. Only use then entire hexadecimal color.  Be conservative. This specification is limited but it is checked by a parser so don't make any mistakes. If you make a mistake, the parser will throw an error and everything will be doomed. Please don't mess up. I want a code response. No comments nor explanations. Only code. I will copy and paste the code.


Here is the specification:
```
start: content | style
content: element*
element: TXT | div | span | p | h1 | h2 | h3 | h4 | h5 | h6 | form | input | button | text_area | label

# elements
div: "<div" "style=" style ">" (content)? "</div>"
span: "<span" "style=" style ">" (content)? "</span>"
p: "<p" "style=" style ">" (content)? "</p>"
h1: "<h1" "style=" style ">" (content)? "</h1>"
h2: "<h2" "style=" style ">" (content)? "</h2>"
h3: "<h3" "style=" style ">" (content)? "</h3>"
h4: "<h4" "style=" style ">" (content)? "</h4>"
h5: "<h5" "style=" style ">" (content)? "</h5>"
h6: "<h6" "style=" style ">" (content)? "</h6>"
form: "<form" "style=" style ">" (content)? "</form>"
text_area: "<textarea" "style=" style ">" (content)? "</textarea>"
label: "<label" "style=" style ">" (content)? "</label>"

input: "<input" "type=" "\"" input_type "\"" "style=" style "/>"
input_type: "text" -> input_text | "password" -> input_password | "email" -> input_email | "number" -> input_number | "date" -> input_date | "checkbox" -> input_checkbox | "radio" -> input_radio | "submit" -> input_submit

button: "<button" "style=" style ">" (content)? "</button>"

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

margin_top_rule: "margin-top:" number unit ";"
margin_bottom_rule: "margin-bottom:" number unit ";"
margin_left_rule: "margin-left:" number unit ";"
margin_right_rule: "margin-right:" number unit ";"

border_radius_rule: "border-radius:" number unit ";"
border_rule: "border:" number unit "solid" COLOR_VALUE ";"

background_rule: "background:" COLOR_VALUE ";"

color_rule: "color:" COLOR_VALUE ";"

# values
number: SIGNED_NUMBER
unit: "px" -> px | "em" -> em | "rem" -> rem | "vw" -> vw | "vh" -> vh | "%" -> percent
TXT: /[^<>]+/
COLOR_VALUE: /\#[0-9a-fA-F]{6}/

%import common.SIGNED_NUMBER
%import common.WS
%ignore WS
```
    """

def ask_api(prompt):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates HTML code based on specifications."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.7,
        )
        content = response.choices[0].message.content
        
        if content.startswith("```html") and content.endswith("```"):
            content = content.strip("```html").strip("```").strip()
        
        return content
    except Exception as e:
        print(f"Error in API call: {e}")
        return None

def get_starting_idx():
    files = os.listdir(samples_dir)
    idxs = [int(file.split("_")[1].split(".")[0]) for file in files if file.startswith("sample_")]
    return max(idxs) + 1 if idxs else 0

def main():
    env = HTMLCSS()
    num_samples = 4
    starting_idx = get_starting_idx()
    for i in range(num_samples):
        theme = get_random_theme()
        prompt = get_prompt(theme)
        response = ask_api(prompt)
        if response is None:
            print(f"Skipping sample {starting_idx + i} due to API error")
            continue
        try:
            env.compile(response)
            with open(os.path.join(samples_dir, f"sample_{starting_idx + i}.html"), "w") as f:
                f.write(response)
            print(f"Successfully generated sample {starting_idx + i}")
        except Exception as e:
            with open(os.path.join(bad_samples_dir, f"sample_{starting_idx + i}.html"), "w") as f:
                f.write(response)
            print(f"Bad sample {starting_idx + i}: {e}")

if __name__ == '__main__':
    main()