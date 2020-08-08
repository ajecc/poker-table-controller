import cv2 
import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import sys
import os
from PIL import Image
from window_grabber import WindowGrabber

class CardIdentifier:
    def __init__(self, card_images):
        self.card_images = card_images

    def crop_borders(self, image):
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

    def find_score(self, card_image, tablemap_area_image):
        tablemap_area_image = self.crop_borders(tablemap_area_image)
        h, w, _ = tablemap_area_image.shape
        tablemap_area_image = cv2.resize(tablemap_area_image, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
        card_image = cv2.resize(card_image, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
        score, _ = ssim(card_image, tablemap_area_image, full=True, multichannel=True)
        return score

    def find_card(self, tablemap_area, window_image):
        tablemap_area_image = WindowGrabber.get_window_area(tablemap_area, window_image)
        best_score = -1 
        best_card_sym = None
        cv2.imwrite(f'debug\\{tablemap_area.label}.png', tablemap_area_image)
        for card_image, card_sym in self.card_images:
            score = self.find_score(card_image, tablemap_area_image)
            if score > best_score:
                best_score = score
                best_card_sym = card_sym
        return best_card_sym
