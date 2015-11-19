import pride
import pride.gui.widgetlibrary

class Prompt(pride.gui.widgetlibrary.Text_Box):
    
    defaults = {"pack_mode" : "main", "prompt" : "\n>>> ", "target_shell" : "->Python->Shell",
                "end_of_field" : 4, "text" : "\n>>> ", "scroll_bars_enabled" : True}
 
    def _set_text(self, value):
        if value and value[-1] == '\n':
            pride.objects[self.target_shell].handle_input(value[self.end_of_field:])
            value = value + self.prompt
            self.end_of_field = len(value)
        super(Prompt, self)._set_text(value)        
    text = property(pride.gui.widgetlibrary.Text_Box._get_text, _set_text)      
    

class Terminal(pride.gui.gui.Application):
       
    def __init__(self, **kwargs):
        super(Terminal, self).__init__(**kwargs)
        self.create("pride.gui.terminal.Prompt")
 