import mpre.gui.widgetlibrary

class Prompt(mpre.gui.widgetlibrary.Text_Box):
    
    defaults = mpre.gui.widgetlibrary.Text_Box.defaults.copy()
    defaults.update({"pack_mode" : "bottom",
                     "prompt" : ">>> "})
    
    def _get_text(self):
        print "Returning: ", self.prompt + super(Prompt, self)._get_text()
        return self.prompt + super(Prompt, self)._get_text()
    text = property(_get_text, mpre.gui.widgetlibrary.Text_Box._set_text)
    

class Terminal(mpre.gui.widgetlibrary.Application):
    
    defaults = mpre.gui.widgetlibrary.Application.defaults.copy()
    
    def __init__(self, **kwargs):
        super(Terminal, self).__init__(**kwargs)
        self.create("mpre.gui.terminal.Prompt")