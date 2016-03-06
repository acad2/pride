# site_config 
# defaults specified here will override defaults defined in the source code
import os
PRIDE_DIRECTORY = os.path.split(os.path.abspath(__file__))[0]
SITE_CONFIG_FILE = __file__ if __file__[-1] != 'c' else __file__[:-1]
del os

pride_interpreter_Shell_defaults = {"startup_definitions" : \
r"""import pride.base
import pride

from pride.utilities import documentation, usage

def open_firefox():
    try:
        import selenium.webdriver
    except ImportError:
        pass
    else:
        return selenium.webdriver.Firefox()
        
def create(instance_type, *args, **kwargs):
    return objects["->Python"].create(instance_type, *args, **kwargs)

def delete(reference):
    objects[reference].delete()       
import pride.audio
#pride.audio.enable()
#import pride.gui
#window = pride.gui.enable()
#
#pbox = objects[window].create("pride.crypto.illustrator.P_Box")
#data = bytearray("\x00" * 8)
#from pride.crypto.ciphertest import block_rotation
#pbox.permute(data, block_rotation)

#graph = objects["->Python->SDL_Window"].create("pride.gui.graph.Audio_Visualizer")
#explorer = objects["->Python->SDL_Window"].create("pride.gui.fileexplorer.File_Explorer")
#objects[window].create("pride.gui.boardgame.Checkers")

"""}


