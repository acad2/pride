import time

import pride.vmlibrary

import asciimatics.screen

class Terminal(pride.vmlibrary.Process):
    
    defaults = {"auto_start" : False}
    
    def __init__(self, **kwargs):
        super(Terminal, self).__init__(**kwargs)                   
        self.screen = asciimatics.screen.Screen.wrapper(lambda screen: None)          
        #self.run_instruction.execute()
        
    def run(self):        
        screen = self.screen
        event = screen.get_event()
        while event is not None:
            if hasattr(event, "key_code"):
                self.handle_keyboard_event(event.key_code)
            else:
                self.handle_mouse_event(event.x, event.y, event.buttons)
            event = screen.get_event()
            
    def handle_keyboard_event(self, ordinal):
        self.line.append(ordinal)
        if ordinal == ord("\n"):
            self.screen.print_at(bytes(self.line), 0, 0)
            self.line = bytearray()
            
    def handle_mouse_event(self, x, y, buttons):
        pass
        
        
if __name__ == "__main__":
    terminal = Terminal()
    