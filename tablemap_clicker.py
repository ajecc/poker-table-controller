from movement import Movement
import time


class TablemapClicker:
    def __init__(self, poker_window, tablemap, lock, trim_floats=False):
        self.movement = Movement(poker_window)
        self.tablemap = tablemap
        self.lock = lock
        self.symbols = None
        self.trim_floats = trim_floats

    def set_symbols(self, symbols):
        self.symbols = symbols

    def find_button(self, button_name):
        for tablemap_area in self.tablemap.tablemap_areas:
            if ('button' in tablemap_area.label) and (button_name in self.symbols[tablemap_area.label].lower()):
                return tablemap_area
        return None
    
    def check(self):
        button = self.find_button('check')     
        if button is None:
            print('could not find check. folding')
            self.fold()
            return
        print('check')
        self.lock.acquire()
        self.movement.click_tablemap_area(button)
        self.movement.move_mouse(10, 10)
        self.lock.release()

    def fold(self):
        button = self.find_button('fold')
        if button is None:
            print('could not find fold. breaking')
            exit(-1)
        print('fold')
        self.lock.acquire()
        self.movement.click_tablemap_area(button)
        self.movement.move_mouse(10, 10)
        self.lock.release()
        
    def call(self):
        button = self.find_button('call')
        if button is None:
            print('could not find call. checking')
            self.check()
            return
        if button is None:
            # TODO: make this one more general
            # button = self.find_button('all in')
            for tablemap_area in self.tablemap.tablemap_areas:
                if 'button1' in tablemap_area.label:
                    button = tablemap_area
                    break
            print('all in')
            self.lock.acquire()
            self.movement.click_tablemap_area(button)
            self.movement.move_mouse(10, 10)
            self.lock.release()
            return
        print('call')
        self.lock.acquire()
        self.movement.click_tablemap_area(button)
        self.movement.move_mouse(10, 10)
        self.lock.release()

    def bet(self, sum):
        button = self.find_button('bet')
        if button is None:
            button = self.find_button('raise')
        if button is None:
            button = self.find_button('all in')
            self.lock.acquire()
            self.movement.click_tablemap_area(button)
            self.movement.move_mouse(10, 10)
            self.lock.release()
            return
        if button is None:
            self.call()
            return
        if button is None:
            print('could not find bet/raise. checking')
            self.check()
            return
        if self.trim_floats:
            sum = int(sum)
        print(f'raise ({sum})')
        edit = None
        for tablemap_area in self.tablemap.tablemap_areas:
            if 'edit' in tablemap_area.label:
                edit = tablemap_area
                break
        assert edit is not None
        self.lock.acquire()
        self.movement.write_tablemap_area(edit, sum)
        self.movement.click_tablemap_area(button)
        self.movement.move_mouse(10, 10)
        self.lock.release()
