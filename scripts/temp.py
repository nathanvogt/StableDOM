from td.environments.webdev import HTML

dsl = """
(Div (Style border: 4px blue, width: 100px, height: 50px)
    (P 'Hello world')
)
(P 'This is a paragraph')
(Div
    (P 'This is a nested paragraph')
    (P 'This is another nested paragraph')
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
