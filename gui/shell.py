import pride
import pride.gui.widgetlibrary    
        
class Prompt(pride.gui.widgetlibrary.Text_Box):
    
    defaults = {"pack_mode" : "main", "prompt" : "\n>>> ", "program" : '',
                "end_of_field" : 4, "text" : '', "scroll_bars_enabled" : True}
 
    required_attributes = ("program", )
    
    def __init__(self, **kwargs):
        super(Prompt, self).__init__(**kwargs)
        self.text = self.text + "\n>>> "
        self.end_of_field = len(self.text)
        
    def _set_text(self, value):
        if value and value[-1] == '\n':
            output = pride.objects[self.program].handle_input(value[self.end_of_field:])
            value = value + (output or self.prompt)
            self.end_of_field = len(value)
        super(Prompt, self)._set_text(value)        
    text = property(pride.gui.widgetlibrary.Text_Box._get_text, _set_text)      
    

class Python_Shell(pride.gui.gui.Application):
               
    def __init__(self, **kwargs):
        super(Python_Shell, self).__init__(**kwargs)
        shell_program = self.create("pride.shell.Python_Shell")        
        self._children.remove(shell_program) # don't try to pack/draw it
        pride.objects[shell_program.shell].stdout = self
        self.prompt = self.create("pride.gui.shell.Prompt", program=shell_program.reference).reference         
    
    def write(self, data):
        pride.objects[self.prompt].text += data