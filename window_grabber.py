from PIL import Image
import PIL.ImageOps
import win32gui
import win32ui
import uuid
import win32con
import win32process
from ctypes import windll
from skimage.metrics import structural_similarity as ssim
import numpy as np
import pytesseract
import imagehash
import cv2
import time
import os


class WindowGrabber:
    def __init__(self, window_identifier_image_path, windows_identified):
        self.IMAGE_NAME = os.path.join('temp', f'capture_{os.getpid()}.bmp') 
        self.window_identifier = cv2.imread(window_identifier_image_path)
        self.windows_identified = windows_identified
        self.poker_window = None
        self.poker_window_tid = None
        self.poker_window_pid = None

    @staticmethod
    def get_window_area(tablemap_area, window_image):
        return window_image[tablemap_area.y: tablemap_area.y + tablemap_area.h - 1, 
                tablemap_area.x: tablemap_area.x + tablemap_area.w - 1].copy()
       
    def get_window_area_text(self, tablemap_area, window_image):
        cropped = WindowGrabber.get_window_area(tablemap_area, window_image)
        cropped = cv2.resize(cropped, (0, 0), fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        cropped = ~cropped
        cropped = cv2.GaussianBlur(cropped, (5, 5), 1)
        cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
        low_white = np.array([150, 150, 150])
        high_white = np.array([255, 255, 255])
        mask = cv2.inRange(cropped, low_white, high_white)
        cropped[mask > 0] = (255, 255, 255)
        cropped[mask <= 0] = (0, 0, 0)
        cropped = Image.fromarray(cropped)
        if 'button' in tablemap_area.label:
            conf = '--psm 6'# -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$¢:.,'
        else:
            conf = '--psm 6'# -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$¢:.,'
        text = pytesseract.image_to_string(cropped, config=conf, lang='eng')
        return text    
    
    def get_window_area_similarity(self, tablemap_area, window_image, other_image):
        return WindowGrabber.get_images_similarity(
                WindowGrabber.get_window_area(tablemap_area, window_image), 
                other_image)

    def search_for_poker_window(self):
        hwnds = self.get_windows()
        for hwnd in hwnds:
            self.grab_image(hwnd)
            candidate_window = cv2.imread(self.IMAGE_NAME)
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
            im.save(self.IMAGE_NAME)

    @staticmethod
    def convert(img):
        img = cv2.resize(img, (0, 0), fx=4, fy=4)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = ~img
        img = cv2.GaussianBlur(img, (5, 5), 1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    @staticmethod
    def get_images_similarity(lhs, rhs):
        op = cv2.TM_SQDIFF_NORMED
        try:
            res = cv2.matchTemplate(lhs, rhs, op)
        except:
            lhs_h, lhs_w, _ = lhs.shape
            rhs_h, rhs_w, _ = rhs.shape
            h = max(lhs_h, rhs_h)
            w = max(lhs_w, rhs_w)
            lhs = cv2.resize(lhs, (h, w), interpolation=cv2.INTER_LINEAR)
            rhs = cv2.resize(rhs, (h, w), interpolation=cv2.INTER_LINEAR)
            res = cv2.matchTemplate(rhs, lhs, op)
        mn, mx, _, _ = cv2.minMaxLoc(res)
        return (1 - mn)

    @staticmethod
    def enum_windows_proc(hwnd, top_windows):
        if win32gui.IsWindowVisible(hwnd):
            top_windows.append(hwnd)
        return True 
