# site_config 
# defaults specified here will override defaults defined in the source code
import os
PRIDE_DIRECTORY = os.path.split(__file__)[0]
SITE_CONFIG_FILE = __file__ if __file__[-1] != 'c' else __file__[:-1]
del os

pride_interpreter_Shell_defaults = {"startup_definitions" : \
r"""import pride.base
import pride

from pride.utilities import documentation

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
#import pride.audio
#pride.audio.enable()
import pride.gui
pride.gui.enable()
"""}

pride_rpc_Rpc_Server_defaults ={'certfile' : 'rpc_server.crt', 'keyfile' : 'rpc_server.key'}

pride_user_User_defaults = {'username' : 'localhost'}
