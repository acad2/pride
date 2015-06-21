import os

if "__file__" not in globals():
    __file__ = os.getcwd()
PACKAGE_LOCATION = os.path.dirname(os.path.abspath(__file__))

SCREEN_SIZE = (800, 600)
MAX_LAYER = int('1' * 64, 2)
R = 0
G = 115
B = 10

def point_in_area(area, position):
    x, y, w, h = area
    point_x, point_y = position
    if point_x >= x and point_x <= x + w:
        if point_y >= y and point_y <= y + h:
            return True
            
def enable():
    import mpre
    mpre.objects["Metapython"].create("mpre.gui.sdllibrary.SDL_Window")  
    mpre.objects["Metapython"].create("mpre.gui.gui.Organizer")                 