from tablemap import Tablemap
from tablemap_grabber import TablemapGrabber
from movement import Movement
import threading
import time
import sys


if __name__ == '__main__':
    tablemap = Tablemap('poker_th.json')
    windows_identified = []
    if len(sys.argv) == 2:
        windows_identified = eval(sys.argv[1])
    TablemapGrabber('images', tablemap, windows_identified) 
