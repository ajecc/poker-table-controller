import os
import sys
from PIL import Image

if __name__ == '__main__':
    dirs = os.listdir('images')
    w, h = None, None
    for path in dirs:
        if len(path) != 6:
            continue
        path = os.path.join('images', path)
        image = Image.open(path)
        if w is None:
            w, h = image.size
            continue
        image = image.resize((w, h), Image.ANTIALIAS)
        image.save(path)
