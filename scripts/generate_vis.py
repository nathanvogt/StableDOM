import matplotlib.pyplot as plt
import numpy as np

def visualize(image_generator):
    plt.ion()
    fig, ax = plt.subplots()

    for image in image_generator():
        ax.imshow(image[0])
        plt.draw()
        plt.pause(0.5)
        ax.clear()