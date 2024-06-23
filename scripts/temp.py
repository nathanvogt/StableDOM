from td.environments.webdev import HTML
from td.environments.csg2da import CSG2DA
from td.environments.csg2d import CSG2D
from td.environments.tinysvgoffset import TinySVGOffset
import matplotlib.pyplot as plt


def main(env):
    env_to_env = {
        "html": HTML(),
        "csg2da": CSG2DA(),
        "csg2d": CSG2D(),
        "tinysvgoffset": TinySVGOffset(),
    }
    env = env_to_env[env]

    html_dsl = """
(Div (Style (Junct border: 2px green width: 100%))
(Compose
(Div (Style (Junct border: 3px blue width: 100%)) (P '12'))
(Compose 
(Div (Style margin-left: 36px) (P 'F'))
(Compose
(Compose
(Div (Style (Junct border: 2px blue (Junct width: 50% (Junct margin-left: auto margin-right: auto))))  (Compose (P '100') (Compose (P '100') (P '100'))))
(Div (Style (Junct width: 24% (Junct margin-right: 8px margin-left: auto))) (P '8'))
)
(Div (Style (Junct border: 2px red (Junct margin-top: 50px width: 100%)))(Div (Style (Junct width: 24% (Junct height: 24px (Junct margin-left: auto margin-right: auto)))) (P '12'))))))
)
"""
    # html_dsl = [
    #     "(Div(Style(Junctborder:2pxgreenwidth:100%))(Compose(Div(Style(Junctborder:3pxbluewidth:100%))(P'12'))(Compose(Div(Stylemargin-left:36px)(P'F'))(Compose(Compose(Div(Style(Junctborder:2pxblue(Junctwidth:50%(Junctmargin-left:automargin-right:auto))))(Compose(P'100')(Compose(P'100')(Compose(P'5')(P'6')))))(Div(Style(Junctmargin-top:Bpx(Junctheight:100%margin-left:auto)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxwidth:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:automargin-right:auto))))(P'12')))))))",
    #     "(Div(Style(Junctborder:2pxgreenwidth:100%))(Compose(Div(Style(Junctborder:3pxbluewidth:100%))(P'12'))(Compose(Div(Stylemargin-left:36px)(P'F'))(Compose(Compose(Div(Style(Junctborder:2pxblue(Junctmargin-left:automargin-bottom:7%)))(Compose(P'100')(Compose(P'100')(P'100'))))(Div(Style(Junctheight:B%border:Apxblue))(P'8')))(Div(Style(Junctmargin-top:automargin-top:auto))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:automargin-right:auto))))(P'12')))))))",
    #     "(Div(Style(Junctborder:2pxgreenwidth:100%))(Compose(Div(Style(Junctborder:3pxbluewidth:100%))(P'12'))(Compose(Div(Stylemargin-left:auto)(P'F'))(Compose(Compose(Div(Style(Junctborder:2pxblue(Junctwidth:50%(Junctmargin-left:automargin-right:auto))))(Compose(P'100')(Compose(P'100')(P'100'))))(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:auto)))(P'8')))(Div(Style(Junctmargin-top:12%(Junctmargin-top:automargin-left:2%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:automargin-right:auto))))(Compose(P'0')(P'1'))))))))",
    # ][-1]
    csg2d_dsl = """
(+ (- (Circle 8 8 8) (Circle 5 8 8)) (Quad 8 8 4 4 H))
"""

    csg2da_dsl = """
(+ (- (Circle 8 6 8) (Circle 5 8 8)) (- (Circle 2 9 A) (Quad 9 A 2 2 H)))
"""

    tinysvgoffset_dsl = """
(Arrange v (Rectangle 9 2 none black 2 +0 +0) (Rectangle 9 4 none green 2 +0 +0) 0)
"""
    tinysvgoffset_dsl = """
(Arrange v (Ellipse 9 9 red none 0 +0 +0) (Arrange v (Ellipse 7 7 orange none 0 +0 +0) (Arrange v (Ellipse 5 5 yellow none 0 +0 +0) (Ellipse 3 3 green none 0 +0 +0) 3) 2) 1)
"""

    dsl = (
        html_dsl
        if env.name() == "html"
        else (
            csg2da_dsl
            if env.name() == "csg2da"
            else csg2d_dsl if env.name() == "csg2d" else tinysvgoffset_dsl
        )
    )

    # ion for interactive (archived)
    plt.ion()
    fig, ax = plt.subplots()

    # uncomment for single render
    # img = env.compile(dsl)
    # ax.imshow(img)
    # ax.set_title(dsl)
    # plt.draw()
    # plt.show()

    dsl1 = ['(Circle 0 0 0)', '(+ (Quad 3 E D C N) (Quad 9 B E 1 N))', '(+ (- (Circle 8 6 8) (Circle 5 8 9)) (Quad 9 B E 1 N))', '(+ (- (Circle 8 6 8) (Circle 5 8 9)) (- (Circle 3 9 9) (Quad 9 A 2 2 L)))', '(+ (- (Circle 8 6 8) (Circle 5 8 9)) (- (Circle 2 9 9) (Quad 9 A 2 2 L)))', '(+ (- (Circle 8 6 8) (Circle 5 8 8)) (- (Circle 2 9 9) (Quad 9 A 2 2 L)))', '(+ (- (Circle 8 6 8) (Circle 5 8 8)) (- (Circle 2 9 A) (Quad 9 A 2 2 L)))']
    dsl2 = ['(Circle 0 0 0)', '(- (Quad F 5 9 3 M) (Circle 7 B 8))', '(- (Quad F 5 9 3 M) (+ (Circle E E F) (Quad 4 7 E 5 L)))', '(- (+ (Circle 8 6 8) (Quad 5 6 7 2 I)) (+ (Circle E E F) (Quad 4 7 E 5 L)))', '(- (+ (Circle 8 6 8) (Quad 5 6 7 2 I)) (+ (Circle E E F) (Circle 2 9 9)))', '(- (+ (Circle 8 6 8) (Quad 5 6 7 2 I)) (+ (- (Circle 6 7 8) (Quad 9 A 2 2 H)) (Circle 2 9 9)))', '(- (+ (Circle 8 6 8) (Quad 5 6 7 2 I)) (+ (- (Circle 6 8 8) (Quad 9 A 2 2 H)) (Circle 2 9 9)))', '(- (+ (Circle 8 6 8) (Quad 5 6 7 2 I)) (+ (- (Circle 6 7 8) (Quad 9 A 2 2 H)) (Circle 2 9 9)))', '(- (+ (Circle 8 6 8) (Quad 5 6 7 2 I)) (+ (- (Circle 5 7 8) (Quad 9 A 2 2 H)) (Circle 2 9 9)))', '(- (+ (Circle 8 6 8) (Quad 5 6 7 2 I)) (+ (- (Circle 5 8 8) (Quad 9 A 2 2 H)) (Circle 2 9 9)))', '(- (+ (Circle 8 6 8) (Quad 5 6 7 2 I)) (+ (- (Circle 5 8 8) (Quad 9 A 2 2 H)) (Circle 2 9 A)))', '(+ (- (Circle 8 6 8) (Circle 5 8 8)) (- (Circle 2 9 A) (Quad 9 9 3 1 H)))', '(+ (- (Circle 8 6 8) (Circle 5 8 8)) (- (Circle 2 9 A) (Quad 9 A 2 2 H)))']
    dsl3 = ['(Circle 0 0 0)', '(+ (Circle 8 F D) (Circle 2 9 A))', '(+ (- (Quad 4 0 4 4 I) (Circle 3 B 3)) (Circle 2 9 A))', '(+ (- (- (Circle 8 6 8) (Circle 3 8 8)) (Circle 3 B 3)) (Circle 2 9 A))', '(+ (- (- (Circle 8 6 8) (Circle 3 8 8)) (Circle 5 B 3)) (Circle 2 9 A))', '(+ (- (- (Circle 8 6 8) (Circle 3 8 8)) (Quad F C 6 6 N)) (Circle 2 9 A))', '(+ (- (- (Circle 8 6 8) (Circle 3 8 8)) (Circle 5 8 8)) (Circle 2 9 A))']
    for dsl in dsl2:
        img = env.compile(dsl)
        ax.imshow(img)
        ax.set_title(dsl)
        plt.draw()
        plt.pause(1)
        ax.clear()


if __name__ == "__main__":
    import sys

    env = sys.argv[1] if len(sys.argv) > 1 else "csg2da"

    main(env)
