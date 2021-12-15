from window import *
import os


if __name__ == '__main__':
    # For Windows
    new_file_explorer(directory=os.environ.get('HOMEDRIVE')+os.environ.get('HOMEPATH'))
