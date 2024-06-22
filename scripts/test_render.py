import imgkit
from IPython.display import display, Image
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image as PILImage
import numpy as np

# Define your HTML and CSS
html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background-color: lightblue;
            font-size: 20px;
            color: white;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>Welcome to My Page</h1>
    <p>This is a sample paragraph in our webpage.</p>
</body>
</html>
"""

# Convert HTML to an image and get the image in byte format
img_raw = imgkit.from_string(html, False, options={"format": "png"})
image = PILImage.open(BytesIO(img_raw))

if image.mode != "RGB":
    image = image.convert("RGB")

desired_width = 800
desired_height = 600
image = image.resize((desired_width, desired_height))

image_np = np.array(image)
print(image_np.shape)

plt.imshow(image_np)
plt.axis("off")
plt.show()
