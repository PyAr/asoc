#!/usr/bin/fades

import os

from PIL import Image  # fades pillow

PICTURES_DIR = 'pictures'

pictpaths = [os.path.join(PICTURES_DIR, f) for f in os.listdir(PICTURES_DIR)]
for pictpath in pictpaths:
    image = Image.open(pictpath)
    if image.width != image.height:
        print(pictpath, image.size)
