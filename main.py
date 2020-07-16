from tablemap import Tablemap
from tablemap_grabber import TablemapGrabber
from movement import Movement
import threading
import time


if __name__ == '__main__':
    tablemap = Tablemap('poker_th.json')
    movement_mutex = threading.Lock()
    TablemapGrabber('images', tablemap, movement_mutex, [])
    while True:
        time.sleep(100000)
