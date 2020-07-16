import math
import pyautogui
import win32gui

class Movement:
    def __init__(self):
        pyautogui.MINIMUM_DURATION = 0
        pyautogui.MINIMUM_SLEEP = 0
        pyautogui.PAUSE = 0

    def get_tablemap_area_absolute_coords(self, hwnd, tablemap_area):
        x, y, _, _ = win32gui.GetWindowRect(hwnd)
        x += tablemap_area.x
        y += tablemap_area.y
        return x, y

    def click_tablemap_area(self, hwnd, tablemap_area):
        x, y = self.get_tablemap_area_absolute_coords(hwnd, tablemap_area)
        win32gui.SetFocus(hwnd)
        self.move_mouse(x, y)
        self.click()

    def write_tablemap_area(self, hwnd, tablemap_area, text):
        x, y = self.get_tablemap_area_absolute_coords(hwnd, tablemap_area)
        win32gui.SetFocus(hwnd)
        self.move_mouse(x, y)
        self.double_click()
        self.keyboard_backspace()
        self.keyboard_write(text)

    def keyboard_write(self, text):
        pyautogui.typewrite(text)

    def keyboard_backspace(self):
        pyautogui.typewrite(['backspace'])
    
    def move_mouse(self, x, y):
        pyautogui.moveTo((x, y))

    def click(self):
        pyautogui.click()

    def double_click(self):
        pyautogui.doubleClick()
