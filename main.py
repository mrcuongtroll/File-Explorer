from window import *
import os


if __name__ == '__main__':
    # FileExplorerWindow()
    curdir = os.getcwd()
    for dir in os.listdir(curdir):
        print(os.stat(dir))