# pride.shell_launcher - configuration file for launching the shell 
import pride

options = {"parse_args" : True,
           "startup_definitions" : '',
           "username" : "localhost",
           "password" : ''}

# feel free to customize
definitions = \
r"""import pride.base
import pride

environment = pride.environment
#objects = pride.objects
from pride.importers import From_Disk
from pride.utilities import documentation

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
    return objects["->Python"].create(instance_type, *args, **kwargs)

def delete(instance_name):
    objects[instance_name].delete()
                                     
def update(instance_name):
    return objects[instance_name].update()
    
#_package = create("pride.package.Package", pride, include_documentation=True)
#with open("metapython.pack", 'wb') as package_file:
#    _package.save(_file=package_file)
#print _package.documentation["pride"].markdown

#_sqlite3 = _package.get_module("sqlite3")
 
#import pride.gui
#pride.gui.enable()
#h = objects["SDL_Window"].create("pride.gui.widgetlibrary.Homescreen")
#t = objects["Task_Bar"]
#i = objects["Indicator"]
##d = objects["Date_Time_Button"]

#import pride.package
#p = pride.package.Package(pride)

#update("->Python")
#update("->Python")
#x = objects["->Python"].save()
#y = pride.base.Base.load(x) # calls .on_load automatically

#z = s(constructor)
#newz = l(z) # does not call .on_load

#sniffer = create("pride.network.Packet_Sniffer")
#import socket

#ssl_server = create("pride.networkssl.SSL_Server")
#ssl_client = create("pride.networkssl.SSL_Client", target=("127.0.0.1", 443))

#objects["->Python"].create("pride.voip.Message_Server")
#client = objects["->Python"].create("pride.voip.Message_Client", username="test", auto_login=False)

#import pride.gui
#pride.gui.enable()
#life = create("pride.Life.Game_Of_Life")

#for x in xrange(1000): 
#    rtt = create("pride.networkutilities.RTT_Test", host_info=("192.168.1.254", 80))   

#Instruction("->User->Shell", "handle_input", "import gc, pprint\nfor item in gc.get_referrers(rtt):\n\tprint\n\tpprint.pprint(item)").execute(priority=5)
    
#for x in xrange(1000): 
#    x = create("pride.shell.Command_Line")
#    x.delete()
    
#import pride.interpreter
#m = pride.interpreter.Python()
#s = m.save()
#import pride.base
#l = pride.base.load(s) 

import pride.gui
#pride.gui.enable()
#$SDL_Window.create("pride.gui.cyvasse.Cyvasse")
#objects["->Python->SDL_Window"].create("pride.gui.fileexplorer.File_Explorer")
#objects["SDL_Window"].create("pride.gui.widgetlibrary.Homescreen")
#objects["->Python->SDL_Window"].create("pride.gui.text_editor.Text_Editor")
#objects["->Python->SDL_Window"].create("pride.gui.terminal.Terminal")
#game_world = objects["SDL_Window"].create("pride.game.gamelibrary.Game_World")
#client = game_world.create("pride.game.gamelibrary.Game_Client")
#$Game_World.test_duel()
#game_world.create("pride.game.levels.Level", room_count=(4, 4), theme="earth")
#level = objects["Level"]

#import pride.audio
#pride.audio.enable()

#import json
#from jsontest import *
#s = json.dumps($Python, cls=Base_Encoder)

#from rnltest import relative_name_lookup
#server = relative_name_lookup("Python.Network.Rpc_Server")  
#import objgraph
#objgraph.show_refs(["->Python"])

#ca = create("pride.catest.CA_Test")
"""

options["startup_definitions"] += definitions

if __name__ == "__main__":
    objects["->User"].create("pride.interpreter.Shell", **options)