from td.environments.webdev import HTML
from td.environments.csg2da import CSG2DA
from td.environments.csg2d import CSG2D
import matplotlib.pyplot as plt


def main(env):
    env_to_env = {"html": HTML(), "csg2da": CSG2DA(), "csg2d": CSG2D()}
    env = env_to_env[env]

    html_dsl = """


(Div (Style (Junct border: 2px green (Junct width: 100% height: 100%)))

(Compose 

(Div (Style (Junct border: 2px red width: 12%)) (P '12'))
(Div (Style (Junct border: 2px blue width: 24%)) (P '24'))

)

)




"""
    csg2d_dsl = """
(+ (Circle 1 0 0) (Circle 2 2 2))
"""

    csg2da_dsl = """
//PUT YOUR DSL CODE HERE
"""
    dsl = (
        html_dsl
        if env.name() == "html"
        else csg2da_dsl if env.name() == "csg2da" else csg2d_dsl
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
