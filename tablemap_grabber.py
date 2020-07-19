from window_grabber import WindowGrabber, IMAGE_NAME
import os
import threading
import time
import cv2
import subprocess
import user_dll


class TablemapGrabber:
    def __init__(self, images_path, tablemap, windows_identified):
        print('in tablemap grabber')
        if len(windows_identified) >= 4:
            return
        self.bbling_scraped = False
        self.windows_identified = windows_identified
        self.tablemap = tablemap
        self.symbols = {}
        self.is_hero_turn_area = None
        for tablemap_area in self.tablemap.tablemap_areas:
            self.symbols[tablemap_area.label] = None
            if tablemap_area.label == 'is_hero_turn':
                self.is_hero_turn_area = tablemap_area
        assert self.is_hero_turn_area is not None
        self.window_grabber = WindowGrabber(os.path.join(images_path, 'identifier.png'), self.windows_identified)
        self.load_images(images_path)
        self.search_for_poker_window(images_path)
        print('found poker window')
        while True:
            self.window_grabber.grab_image(self.window_grabber.poker_window)
            window_image = cv2.imread(IMAGE_NAME)
            if not self.is_hero_turn_checker(window_image):
                self.symbols['is_hero_turn'] = '0' 
                continue
            self.symbols['is_hero_turn'] = '1'
            self.scrape_symbols(window_image)
            print(self.symbols)
            user_dll.update_symbols(self.symbols)
            user_dll.process_query('dll$beep')
            sum = user_dll.process_query('dll$betsize')
            if abs(user_dll.process_query('dll$check') - 1) < 0.1:
                self.check()
            elif abs(user_dll.process_query('dll$fold') - 1) < 0.1:
                self.fold()
            elif abs(user_dll.process_query('dll$call') - 1) < 0.1:
                self.call()
            elif abs(user_dll.process_query('dll$bet') - 1) < 0.1:
                self.bet(sum)
            else:
                raise Exception('Invalid decision by the dll')

    def check(self):
        pass
    
    def fold(self):
        pass

    def call(self):
        pass

    def bet(self, sum):
        pass

    def search_for_poker_window(self, images_path):
        while not self.window_grabber.is_poker_window_valid():
            self.window_grabber.search_for_poker_window()
            time.sleep(2)
        self.windows_identified.append((self.window_grabber.poker_window, self.window_grabber.poker_window_tid, self.window_grabber.poker_window_pid))
        # TODO: check this
        # subprocess.run(['py', '-3', 'main.py', str(self.windows_identified)])

    def load_images(self, images_path):
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
        self.is_hero_turn_image = cv2.imread(os.path.join(images_path, 'is_hero_turn.png'))
        self.is_not_hero_turn_image = cv2.imread(os.path.join(images_path, 'is_not_hero_turn.png'))

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
            elif 'is_hero_turn' in label:
                return
            else:
                raise Exception(f'Label {label} does not correspond to a bool_sym')
            similarity = self.window_grabber.get_window_area_similarity(
                    tablemap_area, window_image, image)
            if similarity > 0.95:
                self.symbols[tablemap_area.label] = '1'
            else:
                self.symbols[tablemap_area.label] = '0' 

    def is_hero_turn_checker(self, window_image):
        # NOTE: this might need tweaking depending on the poker platform used
        return self.window_grabber.get_window_area_similarity(self.is_hero_turn_area, window_image, self.is_not_hero_turn_image) < 0.95

    def scrape_symbols(self, window_image):
        threads = []
        for tablemap_area in self.tablemap.tablemap_areas:
            threads.append(threading.Thread(target=self.fetch_symbol, args=(tablemap_area, window_image,)))
            threads[-1].start()
        for thread in threads:
            thread.join()
        if not self.bbling_scraped:
            for i in range(6):
                label = f'p{i}dealer'
                if self.symbols[label]:
                    j = (i + 2) % 6
                    self.symbols['bblind'] = self.symbols[f'p{j}bet']
                    self.bbling_scraped = True
        # TODO: scrape for buttons
        return True
