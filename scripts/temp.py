from td.environments.webdev import HTML
from td.environments.csg2d import CSG2D
import matplotlib.pyplot as plt


def main(env):
    env_to_env = {"html": HTML(), "csg2d": CSG2D()}
    env = env_to_env[env]

    html_dsl = """
(P'lorem ipsum')(Div(Styleheight:12px)(Div(Styleheight:12px)(Div(Styleborder:24pxred)(P'lorem ipsum'))))(Div(Stylewidth:36px)(Div(Styleborder:4pxblue)(P'lorem ipsum')))(Div(Stylewidth:12px)(Div(Stylewidth:36px)(Div(Styleborder:4pxblue)(Div(Styleborder:12pxblue)(P'lorem ipsum')))))(P'lorem ipsum')(P'lorem ipsum')
"""
    csg2d_dsl = """
(+ (Circle 1 0 0) (Circle 2 2 2))
"""
    dsl = html_dsl if env.name() == "html" else csg2d_dsl

    img = env.compile(dsl)
    print(img.shape)

    plt.imshow(img)
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    import sys

    env = sys.argv[1] if len(sys.argv) > 1 else "html"

    main(env)
