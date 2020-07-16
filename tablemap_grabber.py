from window_grabber import WindowGrabber, IMAGE_NAME
import os
import threading
import time
import cv2


class TablemapGrabber:
    def __init__(self, images_path, tablemap, movement_mutex, windows_identified):
        if len(windows_identified) >= 4:
            return
        self.movement_mutex = movement_mutex
        self.tablemap = tablemap
        self.symbols = {}
        for tablemap_area in self.tablemap.tablemap_areas:
            self.symbols[tablemap_area.label] = None
        self.window_grabber = WindowGrabber(os.path.join(images_path, 'identifier.png'))
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        colors = ['h', 'c', 'd', 's']
        self.cards_images = []
        for rank in ranks:
            for color in colors:
                card = rank + color
                self.cards_images.append((cv2.imread(os.path.join(images_path, f'{card}.png')), card))
        self.cards_images.append((cv2.imread(os.path.join(images_path, 'nocard0.png')), 'nocard'))
        self.cards_images.append((cv2.imread(os.path.join(images_path, 'nocard1.png')), 'nocard'))
        self.active_image = cv2.imread(os.path.join(images_path, 'active.png'))
        self.seated_image = cv2.imread(os.path.join(images_path, 'seated.png'))
        self.dealer_image = cv2.imread(os.path.join(images_path, 'dealer.png'))
        while not self.window_grabber.is_poker_window_valid():
            self.window_grabber.search_for_poker_window()
            time.sleep(2)
        windows_identified.append((self.window_grabber.poker_window, self.window_grabber.poker_window_tid, self.window_grabber.poker_window_pid))
        threading.Thread(target=TablemapGrabber,
                args=(images_path, tablemap, movement_mutex, windows_identified))
        while True:
            self.loop()
            print(self.symbols)

    def fetch_symbol(self, tablemap_area, window_image):
        label = tablemap_area.label
        if not tablemap_area.is_bool_symbol:
            if 'cardface' in label: 
                best_score = 0 
                best_card_sym = None
                for card_image, card_sym in self.cards_images:
                    score = self.window_grabber.get_window_area_similarity(
                            tablemap_area, window_image, card_image)
                    if score > best_score:
                        best_score = score
                        best_card_sym = card_sym 
                self.symbols[tablemap_area.label] = best_card_sym
            else:
                self.symbols[tablemap_area.label] =\
                        self.window_grabber.get_window_area_text(tablemap_area, window_image) 
        else:
            if 'active' in label:
                image = self.active_image
            elif 'seated' in label:
                image = self.seated_image
            elif 'dealer' in label:
                image = self.dealer_image
            else:
                raise Exception(f'Label {label} does not correspond to a bool_sym')
            similarity = self.window_grabber.get_window_area_similarity(
                    tablemap_area, window_image, image)
            if similarity > 0.95:
                self.symbols[tablemap_area.label] = True
            else:
                self.symbols[tablemap_area.label] = False

    def loop(self):
        self.window_grabber.grab_image(self.window_grabber.poker_window)
        window_image = cv2.imread(IMAGE_NAME)
        threads = []
        for tablemap_area in self.tablemap.tablemap_areas:
            threads.append(threading.Thread(target=self.fetch_symbol, args=(tablemap_area, window_image,)))
            threads[-1].start()
        for thread in threads:
            thread.join()
        # TODO: scrape for buttons
        return True
