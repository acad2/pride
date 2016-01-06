# site_config 
# defaults specified here will override defaults defined in the source code

pride_user_User_defaults = {"username" : "localhost"}

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
import pride.audio
pride.audio.enable()    
"""}