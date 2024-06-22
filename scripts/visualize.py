import numpy as np
import matplotlib.pyplot as plt
from eval_td import main

images = np.load('evaluation_output.npy')
num_images = images.shape[0]

rows = int(np.ceil(np.sqrt(num_images)))
cols = int(np.ceil(num_images / rows))

fig, axs = plt.subplots(rows, cols, figsize=(16, 9))

if num_images == 1:
    axs.imshow(images[0])
    axs.axis('off')
    axs.text(0.5, 0.5, '0', fontsize=12, ha='center', va='center', color='white', transform=axs.transAxes)
else:
    for i, ax in enumerate(axs.flat):
        if i < num_images:
            ax.imshow(images[i])
            ax.text(0.5, 0.5, str(i), fontsize=12, ha='center', va='center', color='white', transform=ax.transAxes)
        ax.axis('off')

plt.tight_layout()
plt.show()