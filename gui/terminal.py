import mpre.gui.widgetlibrary

class Prompt(mpre.gui.widgetlibrary.Text_Box):
    
    defaults = mpre.gui.widgetlibrary.Text_Box.defaults.copy()
    defaults.update({"pack_mode" : "bottom",
                     "prompt" : ">>> "})
 
    def _set_text(self, value):
        if value and value[-1] == '\n':
            self.parent.handle_input(self.text)
            value = ''
        super(Prompt, self)._set_text(value)        
    text = property(mpre.gui.widgetlibrary.Text_Box._get_text, _set_text)      
    

class Terminal(mpre.gui.widgetlibrary.Application):
    
    defaults = mpre.gui.widgetlibrary.Application.defaults.copy()
    
    def __init__(self, **kwargs):
        super(Terminal, self).__init__(**kwargs)
        self.create("mpre.gui.terminal.Prompt")
                
    def handle_input(self, source_code):
        mpre.objects["Shell"].handle_input(source_code)