import math
import pyautogui
import win32gui

class Movement:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        pyautogui.MINIMUM_DURATION = 0
        pyautogui.MINIMUM_SLEEP = 0
        pyautogui.PAUSE = 0
        self.can_move = True

    def get_tablemap_area_absolute_coords(self, tablemap_area):
        x, y = win32gui.ClientToScreen(self.hwnd, (tablemap_area.x, tablemap_area.y))
        return x, y

    def click_tablemap_area(self, tablemap_area):
        if not self.can_move:
            return
        x, y = self.get_tablemap_area_absolute_coords(tablemap_area)
        x += 10
        y += 10
        win32gui.SetForegroundWindow(self.hwnd)
        self.move_mouse(x, y)
        self.click()

    def write_tablemap_area(self, tablemap_area, text):
        if not self.can_move:
            return
        text = str(text)
        if '.' in text:
            before_point, after_point = text.split('.')[0], text.split('.')[1]
            if len(after_point) > 2:
                after_point = after_point[:2]
            if len(after_point) > 0 and after_point[-1] == '0':
                after_point = after_point[:-1]
            if len(after_point) > 0 and after_point[-1] == '0':
                after_point = after_point[:-1]
            if len(after_point) > 0:
                text = f'{before_point}.{after_point}'
            else:
                text = before_point
        print(f'writing {text}')
        x, y = self.get_tablemap_area_absolute_coords(tablemap_area)
        win32gui.SetForegroundWindow(self.hwnd)
        self.move_mouse(x, y)
        self.double_click()
        for _ in range(10):
            self.keyboard_right()
        for _ in range(10):
            self.keyboard_backspace()
        self.keyboard_write(text)

    def keyboard_write(self, text):
        pyautogui.typewrite(text)

    def keyboard_right(self):
        pyautogui.typewrite(['right'])
    
    def keyboard_backspace(self):
        pyautogui.typewrite(['backspace'])
    
    def move_mouse(self, x, y):
        pyautogui.moveTo((x, y))

    def click(self):
        pyautogui.click()

    def double_click(self):
        pyautogui.doubleClick()
