import time

import mpre
import mpre.gui.gui as gui
import mpre.gui
import mpre.base as base
Instruction = mpre.Instruction


class Scroll_Bar(gui.Container):    
    
    defaults = gui.Container.defaults.copy()
    defaults.update({"size_scalar" : 20,
                     "max_size" : 100})
                     
    def _get_orientation(self):
        return 'x' if self.pack_mode == "horizontal" else 'y'
    orientation = property(_get_orientation)
    
    def __init__(self, **kwargs):
        super(Scroll_Bar, self).__init__(**kwargs)
        orientation = self.orientation
        self.create("mpre.gui.widgetlibrary.Decrement_Button", target=self.parent_name, attribute=orientation)
        self.create("mpre.gui.widgetlibrary.Scroll_Button", target=self.parent_name, attribute=orientation)
        self.create("mpre.gui.widgetlibrary.Increment_Button", target=self.parent_name, attribute=orientation)
        
    def pack(self, modifiers=None):
        modify = 'h' if self.pack_mode == "horizontal" else 'w'
        super(Scroll_Bar, self).pack(modifiers or 
                                    {modify : min(self.max_size,
                                                  int(getattr(self.parent, modify) / self.size_scalar))})
        
        
class Decrement_Button(gui.Button):            
     
    def _get_amount(self):
        return self.w if self.attribute == 'x' else self.h
    amount = property(_get_amount)
    
    def left_click(self, mouse):
        attribute = self.attribute
        instance = mpre.objects[self.target]
        if self.attribute == 'x':
            instance.texture_window_x -= self.amount
        else:
            print "Scroll texture window up"
            instance.texture_window_y -= self.amount    
        

class Scroll_Button(gui.Button):
    pass        
    """def _get_x(self):
        return super(Scroll_Button, self)._get_x()
    def _set_x(self, value):
        super(Scroll_Button, self)._set_x(value)
        mpre.objects[self.target].texture_window_x += valu
        instance.srcrect = self.x, srcrect[1], srcrect[2], srcrect[3]
    x = property(_get_x, _set_x)
    
    def _get_y(self):
        return super(Scroll_Button, self)._get_y()
    def _set_y(self, value):
        super(Scroll_Button, self)._set_y(value)
        instance = mpre.objects[self.target]
        srcrect = instance.srcrect
        instance.srcrect = srcrect[0], self.y, srcrect[2], srcrect[3]
    y = property(_get_y, _set_y)
    
    def pack(self, modifiers=None):
        super(Scroll_Button, self).pack(modifiers)
        x, y, w, h  = mpre.objects[self.target].srcrect
        if self.attribute == 'x':
            self.x = x
        else:
            self.y = y     """   
        
    
class Increment_Button(gui.Button):            
     
    def _get_amount(self):
        return self.w if self.attribute == "horizontal" else self.h
    amount = property(_get_amount)
    
    def left_click(self, mouse):
        attribute = self.attribute
        instance = mpre.objects[self.target]
        if self.attribute == 'x':
            instance.texture_window_x += self.amount
        else:
            instance.texture_window_y += self.amount       

        
class Indicator(gui.Button):  
    
    defaults = gui.Button.defaults.copy()
    defaults.update({"pack_mode" : "horizontal",
                     "h" : 16,
                     "line_color" : (255, 235, 155)})    
    
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
        mpre.objects[self.target].delete()
        
        
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
       # self.create(Date_Time_Button)
        self.create(Delete_Button, parent_name)
        self.create(Text_Field)
        

class Text_Field(gui.Button):
    
    defaults = gui.Button.defaults.copy()
    defaults.update({"allow_text_edit" : True,
                     "h" : 16,
                     "pack_mode" : "horizontal"})          
        
    def __init__(self, **kwargs):
        super(Text_Field, self).__init__(**kwargs)
        self.create(Scroll_Bar)
        
        
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