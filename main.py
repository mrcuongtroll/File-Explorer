from window import *
import os


"""
To bundle executable version of this program:
    - Install pyinstaller package
    - Open this project folder in terminal
    - Run the following command:
        pyinstaller --onedir -w main.py --runtime-hook addlib.py
"""

if __name__ == '__main__':
    # For Windows
    new_file_explorer(directory=os.environ.get('HOMEDRIVE')+os.environ.get('HOMEPATH'))
