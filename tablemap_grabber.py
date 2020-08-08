from window_grabber import WindowGrabber
from movement import Movement
from tablemap import Tablemap
from card_identifier import CardIdentifier
from tablemap_clicker import TablemapClicker
import os
import threading
import time
import cv2
import subprocess
import user_dll
import multiprocessing


class TablemapGrabber:
    def __init__(self, images_path, tablemap, windows_identified, lock, trim_floats=False, decimal_delim=','):
        if len(windows_identified) >= 4:
            return
        self.images_path = images_path
        self.lock = lock
        self.bbling_scraped = False
        self.windows_identified = windows_identified
        self.tablemap = tablemap
        self.trim_floats = trim_floats
        self.decimal_delim = decimal_delim
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
        self.tablemap_clicker = TablemapClicker(self.window_grabber.poker_window, self.tablemap, self.lock)
        self.card_identifier = CardIdentifier(self.cards_images)
        print('found poker window')
        self.play()

    def play(self):
        while True:
            self.window_grabber.grab_image(self.window_grabber.poker_window)
            window_image = cv2.imread(self.window_grabber.IMAGE_NAME)
            if not self.is_hero_turn_checker(window_image):
                self.symbols['is_hero_turn'] = '0' 
                continue
            time.sleep(1)
            self.symbols['is_hero_turn'] = '1'
            self.scrape_symbols(window_image)
            self.tablemap_clicker.set_symbols(self.symbols)
            user_dll.update_symbols(self.symbols)
            user_dll.process_query('dll$beep')
            sum = user_dll.process_query('dll$betsize')
            # not gonna use an eps here, sue me
            if abs(user_dll.process_query('dll$check') - 1) < 0.1:
                self.tablemap_clicker.check()
            elif abs(user_dll.process_query('dll$call') - 1) < 0.1:
                self.tablemap_clicker.call()
            elif abs(user_dll.process_query('dll$bet') - 1) < 0.1:
                sum = str(float(sum) + 0.001)
                self.tablemap_clicker.bet(sum)
            else:
                raise Exception('Invalid decision by the dll')
            time.sleep(1)

    def search_for_poker_window(self, images_path):
        while not self.window_grabber.is_poker_window_valid():
            self.window_grabber.search_for_poker_window()
            time.sleep(2)
        self.windows_identified.append((self.window_grabber.poker_window, self.window_grabber.poker_window_tid, self.window_grabber.poker_window_pid))
        p = multiprocessing.Process(target=TablemapGrabber, args=(self.images_path, Tablemap('tablemap.json'), self.windows_identified, self.lock, self.trim_floats, self.decimal_delim))
        p.start()

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
        self.not_active_image = cv2.imread(os.path.join(images_path, 'not_active.png'))
        self.not_seated_image = cv2.imread(os.path.join(images_path, 'not_seated.png'))
        self.not_dealer_image = cv2.imread(os.path.join(images_path, 'not_dealer.png'))
        self.is_hero_turn_image = cv2.imread(os.path.join(images_path, 'is_hero_turn.png'))
        self.is_not_hero_turn_image = cv2.imread(os.path.join(images_path, 'is_not_hero_turn.png'))
    
    def strip_bet(self, bet_text):
        if bet_text is None:
            return ''
        if not ('¢' in bet_text or '$' in bet_text):
            return ''
        if ':' in bet_text:
            new_sum = ''
            ok = False
            for c in bet_text:
                if c == ':':
                    ok = True
                    continue
                if ok:
                    new_sum += c
            bet_text = new_sum
        if len(bet_text) == 0:
            return ''
        new_sum = ''
        have_other_sym = False
        for c in bet_text:
            if 'g' == c:
                c = '8'
            if c == '¢' or c == '$' or (ord(c) >= ord('0') and ord(c) <= ord('9')) or c == self.decimal_delim: 
                if c == '0' and have_other_sym:
                    new_sum += c
                if c != '0':
                    new_sum += c
                    if c == '¢' or c == '$':
                        break
                    have_other_sym = True
        bet_text = new_sum
        if len(bet_text) == 0:
            return ''
        cent = False
        if 'c' == bet_text[-1] or '¢' == bet_text[-1] or 'C' == bet_text[-1]:
            cent = True
        new_sum = ''
        for sym in bet_text:
            if (ord(sym) >= ord('0') and ord(sym) <= ord('9')) or sym == self.decimal_delim:
                if sym == self.decimal_delim:
                    sym = '.'
                new_sum += sym
        bet_text = new_sum
        if cent:
            if len(bet_text) == 1:
                bet_text = f'0.0{bet_text}'
            elif len(bet_text) == 2:
                bet_text = f'0.{bet_text}'
        return bet_text

    def fetch_cardface(self, tablemap_area, window_image):
        label = tablemap_area.label
        self.symbols[label] = self.card_identifier.find_card(tablemap_area, window_image)

    def fetch_text(self, tablemap_area, window_image):
        label = tablemap_area.label
        self.symbols[label] =\
                self.window_grabber.get_window_area_text(tablemap_area, window_image) 
        cnt = 0
        while 'button' in label and len(self.symbols[label]) > 15 and cnt < 2:
            time.sleep(0.1)
            self.window_grabber.grab_image(self.window_grabber.poker_window)
            window_image = cv2.imread(self.window_grabber.IMAGE_NAME)
            cnt += 1
            self.symbols[label] =\
                    self.window_grabber.get_window_area_text(tablemap_area, window_image) 
        if self.symbols[label] is None:
            self.symbols[label] = ''
        # stripping reduntant characters from pot
        if 'pot' in label or 'bet' in label or 'balance' in label:
            self.symbols[label] = self.strip_bet(self.symbols[label])

    def fetch_bool_symbol(self, tablemap_area, window_image):
        label = tablemap_area.label
        if 'seated' in label:
            return
        if 'active' in label:
            image = self.active_image
            not_image = self.not_active_image
        elif 'dealer' in label:
            image = self.dealer_image
            not_image = self.not_dealer_image
        elif 'is_hero_turn' in label:
            return
        else:
            raise Exception(f'Label {label} does not correspond to a bool_sym')
        similarity = self.window_grabber.get_window_area_similarity(
                tablemap_area, window_image, image)
        not_similarity = self.window_grabber.get_window_area_similarity(
                tablemap_area, window_image, not_image)
        if similarity > not_similarity:
            if 'dealer' in label:
                if similarity > 0.85:
                    self.symbols[label] = '1'
                else:
                    self.symbols[label] = '0'
            else:
                self.symbols[label] = '1'
        else:
            self.symbols[label] = '0' 
        self.symbols['p2active'] = '1'
        self.symbols['p2seated'] = '1'

    def fetch_symbol(self, tablemap_area, window_image):
        label = tablemap_area.label
        if not tablemap_area.is_bool_symbol:
            if 'cardface' in label: 
                self.fetch_cardface(tablemap_area, window_image)
            else:
                self.fetch_text(tablemap_area, window_image)
        else:
            self.fetch_bool_symbol(tablemap_area, window_image)

    def scrape_bblind(self):
        for i in range(6):
            label = f'p{i}dealer'
            j = i
            bets = 0
            if self.symbols[label] == '1':
                while True:
                    j = (j + 1) % 6
                    if len(self.symbols[f'p{j}bet']) > 0:
                        bets += 1
                    if bets == 2:
                        if j == i:
                            j = (j + 1) % 6
                        self.symbols['bblind'] = self.symbols[f'p{j}bet']
                        if self.symbols['bblind'] != 0:
                            self.bbling_scraped = True
                        else:
                            print('Failed to scrape bblind')
                            exit(-1)
                        return

    def is_hero_turn_checker(self, window_image):
        # NOTE: this might need tweaking depending on the poker platform used
        hero_turn = self.window_grabber.get_window_area_similarity(self.is_hero_turn_area, window_image, self.is_hero_turn_image)
        not_hero_turn = self.window_grabber.get_window_area_similarity(self.is_hero_turn_area, window_image, self.is_not_hero_turn_image) 
        return hero_turn > not_hero_turn and hero_turn > 0.9

    def scrape_symbols(self, window_image):
        threads = []
        for tablemap_area in self.tablemap.tablemap_areas:
            threads.append(threading.Thread(target=self.fetch_symbol, args=(tablemap_area, window_image,)))
            threads[-1].start()
        for thread in threads:
            thread.join()
        if not self.bbling_scraped:
            self.scrape_bblind()
        for i in range(6):
            if (self.symbols[f'p{i}balance'] is not None and self.symbols[f'p{i}balance'] != '0' and len(self.symbols[f'p{i}balance']) > 0) or self.symbols[f'p{i}active'] == '1':
                self.symbols[f'p{i}seated'] = '1'
            else:
                self.symbols[f'p{i}seated'] = '0'
        return True
