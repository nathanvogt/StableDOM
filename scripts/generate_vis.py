import matplotlib.pyplot as plt
import numpy as np

def visualize(step_generator):
    plt.ion()
    fig, ax = plt.subplots()

    for expression, image in step_generator():
        ax.imshow(image[0])
        ax.set_title(expression[0])
        plt.draw()
        plt.pause(1.5)
        ax.clear()