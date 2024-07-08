import os
import matplotlib.pyplot as plt
from td.environments.htmlcss import HTMLCSS, clean_html_whitespace
from td.samplers.mutator import forward_process_with_path
from td.samplers import ConstrainedRandomSampler

samples_dir = "samples"
sample = 1
sample_path = os.path.join(samples_dir, f"sample_{sample}.html")

env = HTMLCSS()
grammar = env.grammar
compiler = env.compiler
sampler = ConstrainedRandomSampler(grammar)

with open(sample_path, "r") as f:
    sample_html = f.read()
    sample_html = sample_html.replace("\n", "")
    sample_html = clean_html_whitespace(sample_html)

img = env.compile(sample_html)

mutated_sample, reverse_mutation, full_path = forward_process_with_path(
    sample_html,
    num_steps=2,
    grammar=grammar,
    sampler=sampler,
    min_primitives=2,
    max_primitives=16,
    path_max_primitives=5,
    selection_max_primitives=16,
    replacement_max_primitives=16,
    p_random=0.2,
    return_full_path=True
)
print(full_path)
print('\n')
print(mutated_sample)
mutated_img = env.compile(mutated_sample)

# show both images side by side
fig, ax = plt.subplots(1, 2)
ax[0].imshow(img)
ax[0].axis("off")
ax[1].imshow(mutated_img)
ax[1].axis("off")
plt.show()
