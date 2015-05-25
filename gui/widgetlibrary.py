import time

import mpre
import mpre.gui.gui as gui
import mpre.gui
import mpre.base as base
Instruction = mpre.Instruction


class Indicator(gui.Button):  
    
    defaults = gui.Button.defaults.copy()
    defaults["pack_mode"] = "horizontal"
    
    def __init__(self, **kwargs):
        super(Indicator, self).__init__(**kwargs)
        self.w = len(mpre.environment.last_creator) * 7
        self.h = 16
        
    def draw_texture(self):
        super(Indicator, self).draw_texture()
        parent = self.parent
        x, y, w, h = parent.area   
        self.w = len(self.parent.instance_name) * 7
        self.h = 16
     
        # draw a line from the top left corner of self to the midpoint of parent
        self.draw("line", (self.x, self.y, x + (w / 2), y + (h / 2)), color=(255, 235, 155))
        self.draw("text", parent.instance_name, color=(255, 255, 255))
                               
        
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
        self.create(Indicator)
        self.create(Text_Field)
        self.create(Date_Time_Button)
        

class Text_Field(gui.Button):
            
    def click(self, mouse):
        if mouse.button == 0:
            self.
    
    
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