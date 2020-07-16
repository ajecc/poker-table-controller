from PIL import Image
import PIL.ImageOps
import win32gui
import win32ui
import win32con
import win32process
from ctypes import windll
import numpy as np
import pytesseract
import imagehash
import cv2
import time
import easyocr

IMAGE_NAME = 'capture.bmp'

class WindowGrabber:
    def __init__(self, window_identifier_image_path, windows_identified):
        self.reader = easyocr.Reader(['en'])
        self.window_identifier = cv2.imread(window_identifier_image_path)
        self.window_identified = windows_identified
        self.poker_window = None
        self.poker_window_tid = None
        self.poker_window_pid = None
    
    def get_window_area(self, tablemap_area, window_image):
        return window_image[tablemap_area.y: tablemap_area.y + tablemap_area.h - 1, 
                tablemap_area.x: tablemap_area.x + tablemap_area.w - 1].copy()
       
    def get_window_area_text(self, tablemap_area, window_image):
        cropped = self.get_window_area(tablemap_area, window_image)
        cropped = cv2.resize(cropped, (0, 0), fx=4, fy=4)
        cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        cropped = ~cropped
        cropped = cv2.GaussianBlur(cropped, (5, 5), 1)
        conf = '-l eng'
        if 'button' in tablemap_area.label:
            conf = '-l eng --psm 6'
        text = pytesseract.image_to_string(cropped, config=conf)
        return text    
    
    def get_window_area_similarity(self, tablemap_area, window_image, other_image):
        return WindowGrabber.get_images_similarity(
                self.get_window_area(tablemap_area, window_image), 
                other_image)

    def search_for_poker_window(self):
        hwnds = self.get_windows()
        for hwnd in hwnds:
            self.grab_image(hwnd)
            candidate_window = cv2.imread(IMAGE_NAME)
            if WindowGrabber.get_images_similarity(candidate_window, self.window_identifier) > 0.95:
                tid, pid = win32process.GetWindowThreadProcessId(hwnd)
                if (hwnd, tid, pid) not in self.windows_identified:
                    self.poker_window = hwnd
                    self.poker_window_tid = tid
                    self.poker_window_pid = pid
                    return        
        self.poker_window = None
    
    def is_poker_window_valid(self):
        if self.poker_window is not None:
            if not win32gui.IsWindow(self.poker_window):
                return False
            new_tid, new_pid = win32process.GetWindowThreadProcessId(self.poker_window)
            return new_tid == self.poker_window_tid and new_pid == self.poker_window_pid
        return False

    def get_windows(self):
        hwnds = []
        windows = []
        win32gui.EnumWindows(WindowGrabber.enum_windows_proc, hwnds)
        for hwnd in hwnds:
            text = win32gui.GetWindowText(hwnd)
            if len(text) > 2:
                windows.append(hwnd)
        return windows

    def grab_image(self, hwnd):
        left, top, right, bot = win32gui.GetClientRect(hwnd)
        w = right - left
        h = bot - top
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
        saveDC.SelectObject(saveBitMap)
        result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        try:
            im = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)
        except:
            im = None
            result = 0
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        if result == 1:
            im.save(IMAGE_NAME)

    @staticmethod
    def get_images_similarity(lhs, rhs):
        try:
            res = cv2.matchTemplate(lhs, rhs, cv2.TM_SQDIFF_NORMED)
        except:
            return 0
        mn, _, _, _ = cv2.minMaxLoc(res)
        return 1 - mn

    @staticmethod
    def enum_windows_proc(hwnd, top_windows):
        if win32gui.IsWindowVisible(hwnd):
            top_windows.append(hwnd)
        return True 
