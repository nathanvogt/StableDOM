import matplotlib.pyplot as plt
from itertools import islice
import numpy as np

def visualize(step_generator):
    plt.ion()
    fig, (ax1, ax2) = plt.subplots(1, 2)
    
    expressions = []
    target_expression, target_image = next(step_generator())

    ax1.imshow(target_image[0], cmap='gray')
    # ax1.set_title(target_expression[0])
    ax1.axis('off')

    for expression, image in islice(step_generator(), 1, None):
        expressions.append(expression[0])

        ax2.imshow(image[0], cmap='gray')
        ax2.set_title(expression[0])
        ax2.axis('off')
        plt.draw()
        plt.pause(0.75)
        ax2.clear()

    # print(expressions)