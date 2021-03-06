import os
import platform

try:
    import sdl2.ext
except ImportError:
    raise
else:
    Color = sdl2.ext.Color
    
if "__file__" not in globals():
    __file__ = os.getcwd()
PACKAGE_LOCATION = os.path.dirname(os.path.abspath(__file__))

SCREEN_SIZE = (800, 600)
MAX_LAYER = int('1' * 64, 2)
R = 0
G = 115
B = 10

def install_pysdl2():
    command = "pip install PySDL2" if platform.system() == "Windows" else "sudo pip install PySDL2"
    os.system(command)
    
def point_in_area(area, position):
    x, y, w, h = area
    point_x, point_y = position
    if point_x >= x and point_x <= x + w:
        if point_y >= y and point_y <= y + h:
            return True
            
def enable():
    import pride
    if "/Python/SDL_Window" not in pride.objects:
        return pride.objects["/Python"].create("pride.gui.sdllibrary.SDL_Window").reference        
    else:
        return "/Python/SDL_Window"
    