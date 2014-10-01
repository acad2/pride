import select
from contextlib import contextmanager
import tty, termios
import base
import defaults
import sys
import codecs

# http://stackoverflow.com/questions/15992651/python-filtered-line-editing-read-stdin-by-char-with-no-echo
# thanks to upside down!
@contextmanager
def cbreak():
    old_attrs = termios.tcgetattr(sys.stdin)
    tty.setraw(sys.stdin.fileno())
    try:    
        yield
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_attrs)

def toggle_echo(fd, enabled):
    (iflag, oflag, cflag, lflag, ispeed, ospeed, cc) = termios.tcgetattr(fd)
    
    if enabled:
        lflag |= termios.ECHO
    else:
        lflag &= ~termios.ECHO
    new_attr = [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
    termios.tcsetattr(fd, termios.TCSANOW, new_attr)        
    
class Keyboard(base.Hardware_Device):
            
    defaults = defaults.Keyboard
        
    def __init__(self, *args, **kwargs):
        super(Keyboard, self).__init__(*args, **kwargs)
        self.thread = self.new_thread()
        self.characters = ""
        
    def input_waiting(self):
        return sys.stdin in select.select([sys.stdin], [], [], 0.0)[0]
        
    def new_thread(self):
        while True:
            with cbreak:
                yield sys.stdin.read(1)
                
    def get_input(self):
        return next(self.thread)
    
    def run(self):
        if self.input_waiting:
            active_item = self.parent.active_item
            hotkey = self.get_hotkey(active_item, self.get_input())
            if hotkey:
                hotkey.post()

        if self in self.parent.objects[self.__class__.__name__]:
            Event("Keyboard", "run").post()
   
    def get_hotkey(self, key, instance):
        if instance is None:
            return None

        hotkey = instance.hotkeys.get(key)
        if not hotkey:
            try:
                hotkey = self.get_hotkey(getattr(instance, "parent"), key)
            except AttributeError:
                self.warning("could not find hotkey from %s or parent" % instance, "Audit: ")

        return hotkey        