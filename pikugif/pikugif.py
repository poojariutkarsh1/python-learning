import imageio.v3 as iio
from PIL import Image
import numpy as np

filenames = ['piku1.png', 'piku2.png']
images = []

size = (500, 500)  # choose whatever size you want

for filename in filenames:
    img = Image.open(filename)
    img = img.resize(size)
    images.append(np.array(img))

iio.imwrite('piku.gif', images, duration=500, loop=0)
