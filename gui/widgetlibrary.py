import time

import mpre
import mpre.gui.gui as gui
import mpre.gui
import mpre.base as base
Instruction = mpre.Instruction

import sdl2

class Attribute_Modifier_Button(gui.Button):

    defaults = gui.Button.defaults.copy()
    defaults.update({"amount" : 0,
                     "method" : "",
                     "target" : None})
                     
    def left_click(self, mouse):        
        instance_name, attribute = self.target
        instance = mpre.objects[instance_name]        
        old_value = getattr(instance, attribute)
        new_value = getattr(old_value, self.method)(self.amount)
        setattr(instance, attribute, new_value)
        self.alert("Modified {}.{}; {}.{}({}) = {}",
                   (instance_name, attribute, old_value, 
                    self.method, self.amount, getattr(instance, attribute)),
                   level='vv')  
                    
 
class Instruction_Button(gui.Button):
    
    defaults = gui.Button.defaults.copy()
    defaults.update({"args" : tuple(),
                     "kwargs" : None,
                     "method" : '',
                     "instance_name" : '',
                     "priority" : 0.0,
                     "host_info" : tuple(),
                     "callback" : None})
                     
    def left_click(self, mouse):
        Instruction(self.instance_name, self.method, 
                    *self.args, **self.kwargs or {}).execute(priority=self.priority, 
                                                             host_info=self.host_info,
                                                             callback=self.callback)
                                             
    
class Method_Button(gui.Button):
        
    defaults = gui.Button.defaults.copy()
    defaults.update({"args" : tuple(),
                     "kwargs" : None,
                     "method" : '',
                     "target" : ''})
                     
    def left_click(self, mouse):
        instance = mpre.objects[self.target]   
        getattr(instance, self.method)(*self.args, **self.kwargs or {})       
                            

class Delete_Button(Method_Button):
    
    defaults = Method_Button.defaults.copy()
    defaults.update({"pack_mode" : "horizontal",
                     "text" : "delete",
                     "method" : "delete"})
        
        
class Homescreen(gui.Window):

    defaults = gui.Window.defaults.copy()
    
    def __init__(self, **kwargs):
        super(Homescreen, self).__init__(**kwargs)
        self.create(Task_Bar)
        

class Task_Bar(gui.Container):

    defaults = gui.Container.defaults.copy()
    defaults.update({"pack_mode" : "menu_bar",
                     "h_range" : (0, 20)})
    
    def __init__(self, **kwargs):
        super(Task_Bar, self).__init__(**kwargs)
        parent_name = self.parent_name
        self.create(Indicator, text=parent_name)
        self.create(Date_Time_Button)
        self.create(Delete_Button, target=parent_name)
        self.create(Text_Box)
        

class Text_Box(gui.Container):
    
    defaults = gui.Container.defaults.copy()
    defaults.update({"h" : 16,
                     "pack_mode" : "horizontal"})          
        
    def __init__(self, **kwargs):
        super(Text_Box, self).__init__(**kwargs)
        text_box_name = self.create(Text_Field).instance_name
        self.create(Scroll_Bar, target=(text_box_name, "texture_window_x"),
                    pack_mode="bottom")         
        self.create(Scroll_Bar, target=(text_box_name, "texture_window_y"),
                    pack_mode="right")
                    

class Text_Field(gui.Button):
            
    defaults = gui.Button.defaults.copy()
    defaults.update({"allow_text_edit" : True,
                     "editing" : False})
    
    def _get_editing(self):
        return self._editing
    def _set_editing(self, value):
        self._editing = value
        if value:
            print "Turning text input on"
            sdl2.SDL_StartTextInput()
        else:
            print "Disabling text input"
            sdl2.SDL_StopTextInput()
    editing = property(_get_editing, _set_editing)
    
    def left_click(self, event):
        self.alert("Left click: {}".format(self.editing))
        self.editing = not self.editing
        
    def draw_texture(self):
        area = self.texture.area
        self.draw("fill", area, color=self.background_color)
        self.draw("rect", area, color=self.color)
        if self.text:
            self.draw("text", self.area, self.text, 
                      bg_color=self.background_color, color=self.text_color)
        
        
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
        

class Color_Palette(gui.Window):
            
    def __init__(self, **kwargs):
        super(Color_Palette, self).__init__(**kwargs)
        color_button = self.create("mpre.gui.gui.Button", pack_mode="horizontal")
        slider_container = self.create("mpre.gui.gui.Container", pack_mode="horizontal")
        
        button_name = color_button.instance_name
        for color in ('r', 'g', 'b'):
            slider_container.create("mpre.gui.widgetlibrary.Scroll_Bar", 
                                    target=(button_name, color))
                                    
                                    
class Scroll_Bar(gui.Container):
                           
    defaults = gui.Container.defaults.copy()
    defaults.update({"pack_mode" : "right"})
    
    def __init__(self, **kwargs):
        super(Scroll_Bar, self).__init__(**kwargs)
        if self.pack_mode in ("right", "horizontal"): # horizontal packs on the left side
            self.w_range = (0, 20)
            pack_mode = "vertical"
        else:
            self.h_range = (0, 20)
            pack_mode = "horizontal"
        options = {"target" : self.target, "pack_mode" : pack_mode}
        self.create(Decrement_Button, **options)
     #   self.create(Scroll_Indicator, **options)
        self.create(Increment_Button, **options)
        
        
class Decrement_Button(Attribute_Modifier_Button):
      
    defaults = Attribute_Modifier_Button.defaults.copy()
    defaults.update({"amount" : 10,
                     "method" : "__sub__"})                 
        
        
class Increment_Button(Attribute_Modifier_Button):
                
    defaults = Attribute_Modifier_Button.defaults.copy()
    defaults.update({"amount" : 10,
                     "method" : "__add__"}) 
                    
                    
class Scroll_Indicator(gui.Button):
            
    defaults = gui.Button.defaults.copy()
    defaults.update({"movable" : True,
                     "text" : ''})
                
    def pack(self, modifiers=None):
        if self.pack_mode in ("right", "horizontal"):
            width = int(self.parent.w * .8)
            self.w_range = (width, width)
        else:
            height = int(self.parent.h * .8)
            self.h_range = (height, height)
        super(Scroll_Indicator, self).pack(modifiers)
        
    def draw_texture(self):
        super(Scroll_Indicator, self).draw_texture()
        self.draw("rect", (self.w / 4, self.h / 4,
                           self.w * 3 / 4, self.h * 3 / 4), color=self.color)
                           
        
class Indicator(gui.Button):  
    
    defaults = gui.Button.defaults.copy()
    defaults.update({"pack_mode" : "horizontal",
                     "h" : 16,
                     "line_color" : (255, 235, 155),
                     "text" : ''})    
    
    def __init__(self, **kwargs):
        super(Indicator, self).__init__(**kwargs)        
        text = self.text = self.text or self.parent_name
        
    def draw_texture(self):
        super(Indicator, self).draw_texture()
        #x, y, w, h = self.parent.area
        
        self.draw("text", self.area, self.text, color=self.text_color, width=self.w)    