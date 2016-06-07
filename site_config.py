""" pride.site_config - site configuration module.

    Site specific defaults, mutable_defaults, flags, and verbosity may be set
    here. Entries take the form of the full name of the object, meaning the
    name of the class, the module the class resides in, and any packages the
    module resides in. Because the '.' symbol denotes attribute access, names
    must have the '.' symbol replaced with '_'. For example:
        
        pride_user_User_defaults = {'username' : 'localhost'}
        
    The above line effectively does the following at runtime, before the class
    is constructed:
    
        pride.user.User.defaults["username"] = "localhost"
        
    This feature is facilitated by the Base metaclass and will work for all
    objects that inherit from Base.
    
    Note that these are the class defaults, meaning that all instances will
    use these values when instantiated (unless the attributes were specified
    explicitly).
    
    For more information on Base objects and default attributes, please see the
    documentation for pride.base.Base 
    
    Temporary customization
    ---------
    The site_config file can be modified temporarily for a single execution via
    command line argument. Simply enter the --site_config flag followed by the
    desired entries, like so:
        
        python -m pride.main --site_config pride_user_User_defaults['username']='Ella'
        
    This will use a different default username for a single execution of the program.
    
    Multiple changes can be made with multiple statements, separated via semicolons:
        
        python -m pride.main --site_config pride_user_User_verbosity['password_verified']=0;pride_user_User_defaults['username']='Ella'            
    """   
# site_config 
# defaults specified here will override defaults defined in the source code
import os
PRIDE_DIRECTORY = os.path.split(os.path.abspath(__file__))[0]
SITE_CONFIG_FILE = __file__ if __file__[-1] != 'c' else __file__[:-1]
del os

import sys
def write_to(entry, **values):    
    site_config_module = sys.modules[__name__]
    if hasattr(site_config_module, entry):
        file_data = "\n{}.update({})\n"
    else:        
        file_data = "\n{} = {}\n"
    file_data.format(entry, str(value))
    with open(SITE_CONFIG_FILE, 'a') as _file:
        _file.write(file_data)
        _file.flush()
        
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
    return objects["/Python"].create(instance_type, *args, **kwargs)

def delete(reference):
    objects[reference].delete()       
#import pride.audio
#pride.audio.enable()
import pride.gui
window = pride.gui.enable()

#graph = objects["/Python/SDL_Window"].create("pride.gui.graph.Graph")
#explorer = objects["/Python/SDL_Window"].create("pride.gui.fileexplorer.File_Explorer")
#chess = objects["/Python/SDL_Window"].create("pride.gui.chess.Chess")
#cyvasse = objects[window].create("pride.gui.cyvasse.Cyvasse")
#messenger = objects[window].create("pride.gui.messenger.Messenger", username="Ella")
#homescreen = objects[window].create('pride.gui.widgetlibrary.Homescreen')
quadword = objects[window].create("pride.gui.grid.Quadword")
"""}


pride_rpc_Rpc_Server_defaults = {'keyfile': 'c:\\users\\_\\pythonbs\\pride\\ssl_server.key', 'certfile': 'c:\\users\\_\\pythonbs\\pride\\ssl_server.crt'}

pride_user_User_defaults = {'username': 'localhost'}
pride_interpreter_Shell_defaults.update({'username': 'localhost', 'startup_definitions': 'import pride.base\nimport pride\n\nfrom pride.utilities import documentation, usage\n\ndef open_firefox():\n    try:\n        import selenium.webdriver\n    except ImportError:\n        pass\n    else:\n        return selenium.webdriver.Firefox()\n        \ndef create(instance_type, *args, **kwargs):\n    return objects["/Python"].create(instance_type, *args, **kwargs)\n\ndef delete(reference):\n    objects[reference].delete()       \n#import pride.audio\n#pride.audio.enable()\nimport pride.gui\nwindow = pride.gui.enable()\n\n#graph = objects["/Python/SDL_Window"].create("pride.gui.graph.Graph")\n#explorer = objects["/Python/SDL_Window"].create("pride.gui.fileexplorer.File_Explorer")\n#chess = objects["/Python/SDL_Window"].create("pride.gui.chess.Chess")\n#cyvasse = objects[window].create("pride.gui.cyvasse.Cyvasse")\n#messenger = objects[window].create("pride.gui.messenger.Messenger", username="Ella")\n#homescreen = objects[window].create(\'pride.gui.widgetlibrary.Homescreen\')\nquadword = objects[window].create("pride.gui.grid.Quadword")\n'})