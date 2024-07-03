import os
import imgkit
from IPython.display import display, Image
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image as PILImage
import numpy as np
from td.environments.htmlcss import HTMLCSS
from td.samplers.mutator import random_mutation
from td.samplers import ConstrainedRandomSampler

samples_dir = "/Users/nathanvogt/tree-diffusion/samples"
sample = 2
sample_path = os.path.join(samples_dir, f"sample_{sample}.html")

env = HTMLCSS()
grammar = env.grammar
compiler = env.compiler
sampler = ConstrainedRandomSampler(grammar)

with open(sample_path, "r") as f:
    sample_html = f.read()
    sample_html = sample_html.replace("\n", "")
img = env.compile(sample_html)

mutation = random_mutation(
    sample_html, grammar, sampler
)
print(mutation)
mutated_sample = mutation.apply(sample_html)
mutated_img = env.compile(mutated_sample)

# show both images side by side
fig, ax = plt.subplots(1, 2)
ax[0].imshow(img)
ax[0].axis("off")
ax[1].imshow(mutated_img)
ax[1].axis("off")
plt.show()