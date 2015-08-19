import mpre

options = {"parse_args" : True,
           "startup_definitions" : '',
           "username" : "localhost",
           "password" : ''}

# feel free to customize
definitions = \
r"""import mpre.base
import mpre

environment = mpre.environment
objects = mpre.objects
from mpre.importers import From_Disk
from mpre.utilities import documentation

__from_disk_importer = From_Disk()
from_disk_import = __from_disk_importer.load_module

def open_firefox():
    try:
        import selenium.webdriver
    except ImportError:
        pass
    else:
        return selenium.webdriver.Firefox()
        
    
#def restart():
    
    
def save(instance_name, _file=None):
    return objects[instance_name].save(_file=None)
    
def create(instance_type, *args, **kwargs):
    return objects["Metapython"].create(instance_type, *args, **kwargs)

def delete(instance_name):
    objects[instance_name].delete()
                                     
def update(instance_name):
    return objects[instance_name].update()
    
#_package = create("mpre.package.Package", mpre, include_documentation=True)
#with open("metapython.pack", 'wb') as package_file:
#    _package.save(_file=package_file)
#print _package.documentation["mpre"].markdown

#_sqlite3 = _package.get_module("sqlite3")
 
#import mpre.gui
#mpre.gui.enable()
#h = objects["SDL_Window"].create("mpre.gui.widgetlibrary.Homescreen")
#t = objects["Task_Bar"]
#i = objects["Indicator"]
##d = objects["Date_Time_Button"]

#import mpre.package
#p = mpre.package.Package(mpre)

#update("Metapython")
#update("Metapython")
#x = objects["Metapython"].save()
#y = mpre.base.Base.load(x) # calls .on_load automatically

#z = s(constructor)
#newz = l(z) # does not call .on_load

#sniffer = create("mpre.network.Packet_Sniffer")
#import socket

#ssl_server = create("mpre.networkssl.SSL_Server")
#ssl_client = create("mpre.networkssl.SSL_Client", target=("127.0.0.1", 443))

#objects["Metapython"].create("mpre.voip.Message_Server")
#client = objects["Metapython"].create("mpre.voip.Message_Client", username="test", auto_login=False)

#import mpre.gui
#mpre.gui.enable()
#life = create("mpre.Life.Game_Of_Life")

#for x in xrange(1000): 
#    rtt = create("mpre.networkutilities.RTT_Test", target=("192.168.1.254", 80))   

#for x in xrange(10000): 
#    x = create("mpre.shell.Command_Line")
#    x.delete()
    
#import mpre._metapython
#m = mpre._metapython.Metapython()
#s = m.save()
#import mpre.base
#l = mpre.base.load(s) 

import mpre.gui
mpre.gui.enable()
#objects["SDL_Window"].create("mpre.gui.widgetlibrary.Homescreen")
game_world = objects["SDL_Window"].create("mpre.game.gamelibrary.Game_World")
$Game_World.test_duel()
#game_world.create("mpre.game.levels.Level", room_count=(4, 4), theme="earth")
#level = objects["Level"]

#import mpre.audio
#mpre.audio.enable()

import json
from jsontest import *
#s = json.dumps($Metapython, cls=Base_Encoder)
"""

options["startup_definitions"] += definitions

if __name__ == "__main__":
    objects["Metapython"].create("mpre._metapython.Shell", **options)