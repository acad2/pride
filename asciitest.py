import time

import pride.vmlibrary

import asciimatics.screen

class Terminal(pride.vmlibrary.Process):
    
    defaults = {"cursor" : '|'}
    mutable_defaults = {"line" : bytearray}
    flags = {"line_count" : -1, "cursor_position" : -1}
    
    def __init__(self, **kwargs):
        super(Terminal, self).__init__(**kwargs)                   
        screen = self.screen = asciimatics.screen.Screen.open()        
        self._blank_line = (b" " * (screen.dimensions[1] - 1)) + "\n"
        self.line.append(self.cursor)
        screen.print_at(self.cursor, 0, 0)
        
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
            screen = self.screen
            dimensions = screen.dimensions                       
            self.line.append(ordinal)     
            width = dimensions[1]
            if ordinal == 13 or len(self.line) == width: 
                self.line_count = min(self.line_count + 1, dimensions[0] - 1)
                self.clear_line(self.line_count)                
                screen.print_at(bytes(self.line), 0, self.line_count)                  
                self.line = bytearray()                              
                                  
                if self.line_count == dimensions[0] - 1:
                ##    #self.line_count = -1   
                ##    #self.clear_line(0)
                    self.screen.scroll_to(self.line_count)                        
#        else:
#            self.alert("Unsupported key: {}", (ordinal, ), level=0)
                                
    def clear_line(self, line_number):
        self.screen.print_at(self._blank_line, 0, line_number)
        
    def clear(self):        
        for line in range(self.screen.dimensions[0]):
            self.screen.print_at(self._blank_line, 0, line)
            
    def handle_mouse_event(self, x, y, buttons):
        pass
        
    def delete(self):
        super(Terminal, self).delete()
        self.screen.close()
        
        
if __name__ == "__main__":
    terminal = Terminal()
    