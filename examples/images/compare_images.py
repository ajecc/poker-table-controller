# Python program to illustrate  
# template matching 
import cv2 
import numpy as np
from skimage.metrics import structural_similarity as ssim
import sys
import os
from PIL import Image
img = cv2.imread('capture.png')

def crop_borders(image):
    smallest_x = float('inf')
    biggest_x = -1
    smallest_y = float('inf')
    biggest_y = -1
    h, w, _ = image.shape
    for x in range(h):
        for y in range(w):
            r, g, b = image[x, y]
            # if not some sort of white
            if not (r > 220 and g > 220 and b > 220): 
                smallest_x = min(smallest_x, x)
                biggest_x = max(biggest_x, x)
                smallest_y = min(smallest_y, y)
                biggest_y = max(biggest_y, y)
    return image[smallest_x:biggest_x + 1, smallest_y:biggest_y + 1]


def find_score(lhs, rhs):
    lhs = crop_borders(lhs)
    #lhs = crop_borders(lhs)
    #rhs = crop_borders(rhs)
    #lhs_h, lhs_w, _ = lhs.shape
    rhs_h, rhs_w, _ = rhs.shape
    #h = max(lhs_h, rhs_h)
    #w = max(lhs_w, rhs_w)
    lhs = cv2.resize(lhs, (rhs_w, rhs_h), interpolation=cv2.INTER_CUBIC)
    #rhs = cv2.resize(rhs, (h, w), interpolation=cv2.INTER_LINEAR)
    #lhs = cv2.cvtColor(lhs, cv2.COLOR_BGR2GRAY)
    #rhs = cv2.cvtColor(rhs, cv2.COLOR_BGR2GRAY)
    score, _ = ssim(rhs, lhs, full=True, multichannel=True)
    return score

dirs = os.listdir('.')
max_score = 0
res = None
for path in dirs:
    if len(path) != 6:
        continue
    card = cv2.imread(path)
    score = find_score(img, card)
    if max_score < score:
        max_score = score
        res = path
    print(f'path={path}, score={score}')
print(res[:3])
