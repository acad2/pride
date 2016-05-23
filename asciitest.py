import time

import pride.vmlibrary

import asciimatics.screen

class Terminal(pride.vmlibrary.Process):
        
    mutable_defaults = {"line" : bytearray}
    
    def __init__(self, **kwargs):
        super(Terminal, self).__init__(**kwargs)                   
        asciimatics.screen.Screen.wrapper(self.set_screen)          
                
    def set_screen(self, screen):
        self.screen = screen               
        screen.refresh()
        
    def run(self):        
        screen = self.screen
        event = screen.get_event()
        while event is not None:
            #self.alert("Got event: {}", (event, ), level=0)
            if hasattr(event, "key_code"):
                self.handle_keyboard_event(event.key_code)
            else:
                self.handle_mouse_event(event.x, event.y, event.buttons)
            event = screen.get_event()
        screen.refresh()
        sys.stdout.flush()
        
    def handle_keyboard_event(self, ordinal):
        if ordinal > 0:
            self.line.append(ordinal)
            if ordinal == 13: # return            
                self.screen.print_at(bytes(self.line), 0, 0)
                self.line = bytearray()
#        else:
#            self.alert("Unsupported key: {}", (ordinal, ), level=0)
            
    def handle_mouse_event(self, x, y, buttons):
        pass
        
        
if __name__ == "__main__":
    terminal = Terminal()
    