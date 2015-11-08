import pride.gui.widgetlibrary

class Prompt(pride.gui.widgetlibrary.Text_Box):
    
    defaults = {"pack_mode" : "bottom",
                "prompt" : ">>> "}
 
    def _set_text(self, value):
        if value and value[-1] == '\n':
            self.parent.handle_input(self.text)
            value = ''
        super(Prompt, self)._set_text(value)        
    text = property(pride.gui.widgetlibrary.Text_Box._get_text, _set_text)      
    

class Terminal(pride.gui.gui.Application):
       
    def __init__(self, **kwargs):
        super(Terminal, self).__init__(**kwargs)
        self.create("pride.gui.terminal.Prompt")
                
    def handle_input(self, source_code):
        pride.objects["->Python->Shell"].handle_input(source_code)