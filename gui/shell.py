import pride
import pride.gui.widgetlibrary    
        
class Prompt(pride.gui.widgetlibrary.Text_Box):
    
    defaults = {"pack_mode" : "main", "prompt" : "\n>>> ", "program" : '',
                "end_of_field" : len("\n>>> "), "text" : '', "scroll_bars_enabled" : True}                  
 
    required_attributes = ("program", )
    
    def __init__(self, **kwargs):
        super(Prompt, self).__init__(**kwargs)
        self.text = self.text + "\n>>> "
        self.end_of_field = len(self.text)            
    
    def handle_return(self):
        output = pride.objects[self.program].handle_input(self.text[self.end_of_field:]) # slice off excess i.e. the prompt            
        self.text += (output or self.prompt)
        self.end_of_field = len(self.text)
        
        
class Python_Shell(pride.gui.gui.Application):
               
    def __init__(self, **kwargs):
        super(Python_Shell, self).__init__(**kwargs)
        shell_connection = self.create("pride.interpreter.Shell", username="localhost2", startup_definitions='')
        shell_program = self.create("pride.shell.Python_Shell", shell=shell_connection.reference)        
        self.create("pride.gui.shell.Prompt", program=shell_program.reference)
        
        self._children.remove(shell_connection) # don't try to pack/draw
        self._children.remove(shell_program) 
        
        
        