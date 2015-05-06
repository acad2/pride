import os

if "__file__" not in globals():
    __file__ = os.getcwd()
PACKAGE_LOCATION = os.path.dirname(os.path.abspath(__file__))

SCREEN_SIZE = (800, 600)
MAX_LAYER = int('1' * 64, 2)
R = 0
G = 115
B = 10

