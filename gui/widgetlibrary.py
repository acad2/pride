import time

import mpre
import mpre.gui.gui as gui
import mpre.gui
import mpre.base as base
Instruction = mpre.Instruction


class Indicator(gui.Button):  
    
    defaults = gui.Button.defaults.copy()
    defaults.update({"pack_mode" : "horizontal",
                     "h" : 16,
                     "line_color" : (255, 235, 155),
                     "background_color" : (15, 25, 225, 225)})    
    
    def __init__(self, **kwargs):
        super(Indicator, self).__init__(**kwargs)        
        text = self.text = self.parent_name
        
    def draw_texture(self):
        super(Indicator, self).draw_texture()
        x, y, w, h = self.parent.area
        
        # draw a line from the top left corner of self to the midpoint of parent
        #self.draw("line", (self.x, self.y, x + (w / 2), y + (h / 2)), color=self.line_color)
        self.draw("text", self.area, self.text, color=self.text_color, width=self.w)
                               

class Delete_Button(gui.Button):
    
    defaults = gui.Button.defaults.copy()
    defaults.update({"pack_mode" : "horizontal",
                     "text" : 'delete'})
    
    def __init__(self, target, **kwargs):
        super(Delete_Button, self).__init__(**kwargs)
        self.target=target
                
    def left_click(self, mouse):
        mpre.components[self.target].delete()
        
        
class Homescreen(gui.Window):

    defaults = gui.Window.defaults.copy()
    
    def __init__(self, **kwargs):
        super(Homescreen, self).__init__(**kwargs)
        self.create(Task_Bar)
                

class Task_Bar(gui.Container):

    defaults = gui.Container.defaults.copy()
    defaults["pack_mode"] = "menu_bar"
    
    def __init__(self, **kwargs):
        super(Task_Bar, self).__init__(**kwargs)
        parent_name = self.parent_name
        self.create(Indicator)
        self.create(Date_Time_Button)
        self.create(Delete_Button, parent_name)
        self.create(Text_Field)
        

class Text_Field(gui.Button):
    
    defaults = gui.Button.defaults.copy()
    defaults.update({"allow_text_edit" : True,
                     "h" : 16,
                     "pack_mode" : "horizontal"})
    
    def pack(self, modifiers=None):
        super(Text_Field, self).pack(modifiers)        
     #   self.w = min(self.w, len(self.text) * 12)              
        
    
class Date_Time_Button(gui.Button):

    defaults = gui.Button.defaults.copy()
    defaults.update({"pack_mode" : "horizontal"})

    def __init__(self, **kwargs):
        super(Date_Time_Button, self).__init__(**kwargs)        
        update = self.update_instruction = Instruction(self.instance_name, "update_time")        
        self.update_time()        
  
    def update_time(self):
        self.text = time.asctime()
        instance_name = self.instance_name
        
        self.texture_invalid = True
        self.update_instruction.execute(priority=1)   