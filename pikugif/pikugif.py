# before writing this code, the photos need to be in the same folder

import imageio.v3 as iio
from PIL import Image
import numpy as np

filenames = ['piku1.png', 'piku2.png']  #the names should be exactly of the photos that you have put 
images = []

size = (500, 500)  # this lets us resize the photo here. So done by pillow

for filename in filenames:
    img = Image.open(filename)
    img = img.resize(size)
    images.append(np.array(img))

iio.imwrite('piku.gif', images, duration=500, loop=0)  #made piku's gif yayayya
