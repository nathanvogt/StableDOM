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
    csg2d_dsl = """
(+ (- (Circle 8 8 8) (Circle 5 8 8)) (Quad 8 8 4 4 H))
"""

    csg2da_dsl = """
//PUT YOUR DSL CODE HERE
"""

    tinysvgoffset_dsl = """
(Arrange v (Rectangle 9 2 none black 2 +0 +0) (Rectangle 9 4 none green 2 +0 +0) 0)
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

    img = env.compile(dsl)
    print(img.shape)
    plt.imshow(img)
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    import sys

    env = sys.argv[1] if len(sys.argv) > 1 else "html"

    main(env)
