from td.environments.webdev import HTML

dsl = """

(Div (Style border: 12px blue width: 24px height: 36px)
    (P 'lorem ipsum')
)
(P 'lorem ipsum')
(Div
    (P 'lorem ipsum')
    (P 'lorem ipsum')
)
"""

html = HTML()

img = html.compile(dsl)

# display img
import matplotlib.pyplot as plt

# make the background white
# img[img == 0] = 255
plt.imshow(img)
plt.axis("off")
plt.show()
