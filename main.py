from tablemap import Tablemap
from tablemap_grabber import TablemapGrabber
from movement import Movement
import threading
import time
import sys
import multiprocessing
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-tf', '--trim_floats', required=False, action='store_true',
            help='Trims the decimals from the bet size')
    args = parser.parse_args()
    trim_floats = False
    if args.trim_floats:
        trim_floats = True
    tablemap = Tablemap('tablemap.json')
    windows_identified = []
    lock = multiprocessing.Lock()
    TablemapGrabber('images', tablemap, windows_identified, lock, trim_floats) 
