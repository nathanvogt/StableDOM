from td.environments.webdev import HTML
import matplotlib.pyplot as plt


dsl = """
(Div (Style border: 4px blue height: 24px) (P 'lorem ipsum'))
"""

html = HTML()

img = html.compile(dsl)
print(img.shape)

plt.imshow(img)
plt.axis("off")
plt.show()
