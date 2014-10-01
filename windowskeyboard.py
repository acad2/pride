from msvcrt import kbhit, getwch
import base
import defaults

class Keyboard(base.Hardware_Device):
    
    defaults = defaults.Keyboard
    
    input_waiting = kbhit
    _get_input = getwch
    
    def __init__(self, *args, **kwargs):
        super(Keyboard, self).__init__(*args, **kwargs)
        self.thread = self.new_thread()
      
    def get_input(self):
        return next(self.thread)
        
    def new_thread(self):
        while True:
            yield self._get_input()
            
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