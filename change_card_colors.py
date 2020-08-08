import os
import sys
from PIL import Image
import numpy as np

if __name__ == '__main__':
    dirs = os.listdir('images')
    w, h = None, None
    for path in dirs:
        if len(path) != 6:
            continue
        path = os.path.join('images', path)
        image = Image.open(path)
        image = image.convert('RGBA')
        data = np.array(image)
        red, green, blue, alpha = data.T
        white_areas = (red > 230) & (green > 230) & (blue > 230)
        data[..., :-1][white_areas.T] = (4, 240, 50)
        image = Image.fromarray(data)
        image.save(path)
