import time

import pride
import pride.gui.gui as gui
import pride.gui
import pride.base as base
Instruction = pride.Instruction

import sdl2

class Attribute_Modifier_Button(gui.Button):

    defaults = {"amount" : 0, "operation" : "",  "target" : None}
                     
    def left_click(self, mouse):        
        instance_name, attribute = self.target
        instance = pride.objects[instance_name]        
        old_value = getattr(instance, attribute)
        new_value = getattr(old_value, self.operation)(self.amount)
        setattr(instance, attribute, new_value)
        self.alert("Modified {}.{}; {}.{}({}) = {}",
                   (instance_name, attribute, old_value, 
                    self.operation, self.amount, getattr(instance, attribute)),
                   level='vv')  
                    
 
class Instruction_Button(gui.Button):
    
    defaults = {"args" : tuple(), "kwargs" : None, "method" : '',
                "instance_name" : '', "priority" : 0.0, "callback" : None}
                     
    def left_click(self, mouse):
        Instruction(self.instance_name, self.method, 
                    *self.args, **self.kwargs or {}).execute(priority=self.priority, 
                                                             callback=self.callback)
                                             
    
class Method_Button(gui.Button):
        
    defaults = {"args" : tuple(), "kwargs" : None, "method" : '', "target" : ''}
    flags = {"scale_to_text" : True}.items()
    
    def left_click(self, mouse):
        try:
            instance = self.target()
        except TypeError:
            instance = pride.objects[self.target]  
        getattr(instance, self.method)(*self.args, **self.kwargs or {})     
                            

class Delete_Button(Method_Button):
    
    defaults = {"pack_mode" : "right", "text" : "x", "method" : "delete"}
    flags = {"scale_to_text" : True}.items()
    
        
class Exit_Button(Delete_Button):
        
    defaults = {"text" : "exit"}
    

class Popup_Button(gui.Button):
        
    defaults = {"popup_type" : '', "_popup" : None}
        
    def left_click(self, mouse):
        if self._popup:
            self._popup.delete()
        elif self.popup_type:
            self.alert("Creating: {}".format(self.popup_type), level='vv')
            self._popup = self.create(self.popup_type)
        
        
class Homescreen(gui.Window):
    
    def __init__(self, **kwargs):
        super(Homescreen, self).__init__(**kwargs)
        self.create(Task_Bar, startup_components=\
                                ("pride.gui.widgetlibrary.Date_Time_Button",
                                 "pride.gui.widgetlibrary.Text_Box"))
        

class Task_Bar(gui.Container):

    defaults = {"pack_mode" : "top", "bound" : (0, 20)}
    
    def _set_pack_mode(self, value):
        super(Task_Bar, self)._set_pack_mode(value)
        if self.pack_mode in ("right", "left", "left"):
            self._backup_w_range = self.w_range
            self.w_range = self.bound
            self.h_range = self._backup_h_range
        else:
            self._backup_h_range = self.h_range
            self.h_range = self.bound      
            try:
                self.w_range = self._backup_w_range
            except AttributeError:
                pass
    pack_mode = property(gui.Container._get_pack_mode, _set_pack_mode)
    
    def __init__(self, **kwargs):  
        super(Task_Bar, self).__init__(**kwargs)        
        parent_name = self.parent_name
        self.create(Indicator, text=parent_name)
        self.create(Delete_Button, target=parent_name)
             
 #   def pack(self, modifiers=None):

  #      super(Task_Bar, self).pack(modifiers)
        
        
class Text_Box(gui.Container):
    
    defaults = {"h" : 16, "pack_mode" : "left",
                "allow_text_edit" : True,  "editing" : False}
    
    def _get_editing(self):
        return self._editing
    def _set_editing(self, value):            
        self._editing = value
        if value:
            self.alert("Turning text input on", level='vv')
            sdl2.SDL_StartTextInput()
        else:
            self.alert("Disabling text input", level='vv')
            sdl2.SDL_StopTextInput()
    editing = property(_get_editing, _set_editing) 
         
    def left_click(self, event):
        self.alert("Left click: {}".format(self.editing), level='vvv')
        self.editing = not self.editing
        
    def draw_texture(self):
        area = self.texture.area
        self.draw("fill", area, color=self.background_color)
        self.draw("rect", area, color=self.color)
        if self.text:
            self.draw("text", self.area, self.text, 
                      bg_color=self.background_color, color=self.text_color)
        
                
class Date_Time_Button(gui.Button):

    defaults = {"pack_mode" : "left"}

    def __init__(self, **kwargs):
        super(Date_Time_Button, self).__init__(**kwargs)        
        update = self.update_instruction = Instruction(self.instance_name, "update_time")        
        self.update_time()        
  
    def update_time(self):
        self.text = time.asctime()     
        self.update_instruction.execute(priority=1)   
        

class Color_Palette(gui.Window):
            
    def __init__(self, **kwargs):
        super(Color_Palette, self).__init__(**kwargs)
        color_button = self.create("pride.gui.gui.Button", pack_mode="left")
        slider_container = self.create("pride.gui.gui.Container", pack_mode="left")
        
        button_name = color_button.instance_name
        for color in ('r', 'g', 'b'):
            slider_container.create("pride.gui.widgetlibrary.Scroll_Bar", 
                                    target=(button_name, color))
                                    
                                    
class Scroll_Bar(gui.Container):
                           
    defaults = {"pack_mode" : "right"}
    
    def __init__(self, **kwargs):
        super(Scroll_Bar, self).__init__(**kwargs)
        _target = self.target
        if self.pack_mode in ("right", "left"): # horizontal packs on the left side
            self.w_range = (0, 8)  
            pack_mode = "top"
            #crement_pack_mode = "bottom"
        else:
            self.h_range = (0, 8)
            pack_mode = "left"
            #increment_pack_mode = "right"
        self.create(Decrement_Button, target=_target, pack_mode=pack_mode)
     #   self.create(Sc+roll_Indicator, **options)
        self.create(Increment_Button, target=_target, pack_mode=pack_mode)
        
        
class Decrement_Button(Attribute_Modifier_Button):
      
    defaults = {"amount" : 10, "operation" : "__sub__", "h_range" : (0, 8), "w_range" : (0, 8)}
        
        
class Increment_Button(Attribute_Modifier_Button):
                
    defaults = {"amount" : 10, "operation" : "__add__", "h_range" : (0, 8), "w_range" : (0, 8)}
                    
                    
class Scroll_Indicator(gui.Button):
            
    defaults = {"movable" : True, "text" : ''}
                
    def pack(self, modifiers=None):
        if self.pack_mode in ("right", "left"):
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
    
    defaults = {"pack_mode" : "left",
                "h" : 16,
                "line_color" : (255, 235, 155),
                "text" : ''}
    
    def __init__(self, **kwargs):
        super(Indicator, self).__init__(**kwargs)        
        self.text = self.text or self.parent_name
        
    def draw_texture(self):
        super(Indicator, self).draw_texture()
        #x, y, w, h = self.parent.area
        
        self.draw("text", self.area, self.text, color=self.text_color, width=self.w)    
        

class Done_Button(gui.Button):
        
    def left_click(self, mouse):
        callback_owner, method = self.callback
        getattr(pride.objects[callback_owner], method)()        
        
      
class Prompt(Text_Box):
    
    defaults = {"use_done_button" : False, }
    
    def __init__(self, **kwargs):
        super(Prompt, self).__init__(**kwargs)
        self._use_text_entry_callback = True
        if self.use_done_button:
            self.create("pride.gui.widgetlibrary.Done_Button", 
                        callback=self._done_callback)
                        
    def text_entry(self, value):
        self._text = value
        if value and value[-1] == '\n':
            callback_owner, method = self.callback
            getattr(pride.objects[callback_owner], method)(self.text)
            
    def _done_callback(self):
        self.text += '\n'
        
        
class Dialog_Box(gui.Application):
        
    defaults = {"callback_owner" : '', "callback" : ''}
                     
    def __init__(self, **kwargs):
        super(Application, self).__init__(**kwargs)
        self.create("pride.gui.widgetlibrary.Text_Box", text=self.text,
                    allow_text_edit=False)
        self.user_text = self.create("pride.gui.widgetlibrary.Prompt",
                                     use_done_button=True,
                                     callback=(self.instance_name, "handle_input"))
   
    def handle_input(self, user_input):
        getattr(pride.objects[self.callback_owner], self.callback)(user_input)       
        