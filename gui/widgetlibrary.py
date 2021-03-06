import time

import pride
import pride.gui.gui as gui
import pride.gui
import pride.base as base
Instruction = pride.Instruction

import sdl2

class Attribute_Modifier_Button(gui.Button):

    defaults = {"amount" : 0, "operation" : "",  "target" : None}
                
    verbosity = {"left_click" : 'v'}
    
    def left_click(self, mouse):        
        reference, attribute = self.target
        instance = pride.objects[reference]        
        old_value = getattr(instance, attribute)
        new_value = getattr(old_value, self.operation)(self.amount)
        setattr(instance, attribute, new_value)
        self.alert("Modified {}.{}; {}.{}({}) = {}",
                   (reference, attribute, old_value, 
                    self.operation, self.amount, getattr(instance, attribute)),
                   level=self.verbosity["left_click"])  
                    
 
class Instruction_Button(gui.Button):
    
    defaults = {"args" : tuple(), "kwargs" : None, "method" : '',
                "reference" : '', "priority" : 0.0, "callback" : None}
                     
    def left_click(self, mouse):
        Instruction(self.reference, self.method, 
                    *self.args, **self.kwargs or {}).execute(priority=self.priority, 
                                                             callback=self.callback)
                                             
    
class Method_Button(gui.Button):
        
    defaults = {"args" : tuple(), "kwargs" : None, "method" : '', "target" : ''}
    flags = {"scale_to_text" : True}
    
    def left_click(self, mouse):
        try:
            instance = self.target()
        except TypeError:
            instance = pride.objects[self.target]  
        getattr(instance, self.method)(*self.args, **self.kwargs or {})     
                            

class Delete_Button(Method_Button):
    
    defaults = {"pack_mode" : "right", "text" : "x", "method" : "delete"}
    flags = {"scale_to_text" : True}
    
        
class Exit_Button(Delete_Button):
        
    defaults = {"text" : "exit"}
    

class Popup_Button(gui.Button):
        
    defaults = {"popup_type" : '', "_popup" : None}    
        
    def left_click(self, mouse):
        if self._popup:
            self.alert("Deleting: {}".format(self._popup), level=0)
            self._popup.delete()
        elif self.popup_type:
            self.alert("Creating: {}".format(self.popup_type), level=0)#'vv')
            popup = self._popup = self.create(self.popup_type)
            popup.pack()
            
        
class Objects_Explorer(pride.gui.gui.Application):
    
    def __init__(self, **kwargs):
        super(Objects_Explorer, self).__init__(**kwargs)
        references = self.application_window.create("pride.gui.gui.Container", pack_mode="left", 
                                                             scroll_bars_enabled=True)
        viewer = self.object_attributes_viewer = self.application_window.create("pride.gui.gui.Container", pack_mode="right")
        viewer.current_object = viewer.create("pride.gui.pyobjecttest.Object_Button", objects["/Python"]).reference
        
        for key, item in pride.objects.items():
            references.create("pride.gui.pyobjecttest.Object_Button", item, 
                              opener=viewer.reference, h_range=(20, 20),
                              wrap_text=False)
            
        
class Icon(pride.gui.gui.Button):
            
    defaults = {"h_range" : (0, 40), "w_range" : (0, 40), "pack_mode" : "grid"}
    required_attributes = ("popup_type", )
    
    def left_click(self, mouse):
        if mouse.clicks == 2:
            popup = self.parent.create(self.popup_type)
            popup.pack()
            
    
class Program_Icon(Icon):
    
    defaults = {"program" : '', "popup_type" : ''}
    
    required_attributes = ("program", )
    
    def left_click(self, mouse):
        if mouse.clicks == 2:
            popup = self.parent.create(self.popup_type, program=self.program)
            popup.pack()
            
            
class Homescreen(gui.Application):
    
    def __init__(self, **kwargs):
        super(Homescreen, self).__init__(**kwargs)
        self.application_window.create(Task_Bar, startup_components=("pride.gui.widgetlibrary.Date_Time_Button",
                                                  "pride.gui.widgetlibrary.Text_Box"))        
        self.application_window.create(Icon, popup_type=Objects_Explorer, text="Objects Explorer")
        self.application_window.create(Program_Icon, popup_type="pride.gui.shell.Python_Shell",
                                       program="/User/Command_Line/Python_Shell", text="Python")
        self.application_window.create("pride.gui.text_editor.Shortcut")

        
class Task_Bar(gui.Container):

    defaults = {"pack_mode" : "top"}
    flags= {"bound" : (0, 20)}
    
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
       # width, height = pride.gui.SCREEN_SIZE#self.texture.area
        area = self.area#(0, 0, width, height)
        self.draw("fill", area, color=self.background_color)
        self.draw("rect", area, color=self.color)
        if self.text:
            self.draw("text", self.area, self.text, 
                      bg_color=self.background_color, color=self.text_color)
        
                
class Date_Time_Button(gui.Button):

    defaults = {"pack_mode" : "left", "refresh_interval" : 59.9}

    def __init__(self, **kwargs):
        super(Date_Time_Button, self).__init__(**kwargs)        
        update = self.update_instruction = Instruction(self.reference, "update_time")        
        self.update_time()        
  
    def update_time(self):
        text = time.asctime()    
        self.text = text[:-8] + text[-5:] # remove seconds
        self.update_instruction.execute(priority=self.refresh_interval)   
        
    def delete(self):        
        self.update_instruction.unschedule()        
        super(Date_Time_Button, self).delete()
        
        
class Color_Palette(gui.Window):
            
    def __init__(self, **kwargs):
        super(Color_Palette, self).__init__(**kwargs)
        color_button = self.create("pride.gui.gui.Button", pack_mode="left")
        slider_container = self.create("pride.gui.gui.Container", pack_mode="left")
        
        button_name = color_button.reference
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
        
    defaults = {"w_range" : (0, 20), "h_range" : (0, 20), "pack_mode" : "right"}
    def left_click(self, mouse):
        callback_owner, method = self.callback
        getattr(pride.objects[callback_owner], method)()        
        
      
class Prompt(Text_Box):
    
    defaults = {"use_done_button" : False}
    
    def __init__(self, **kwargs):
        super(Prompt, self).__init__(**kwargs)
        if self.use_done_button:
            self.create("pride.gui.widgetlibrary.Done_Button", callback=(self.reference, "_done_callback"))
                        
    def text_entry(self, value):
        self._text = value
        if value and value[-1] == '\n':
            callback_owner, method = self.callback
            getattr(pride.objects[callback_owner], method)(self.text)
            self._text = ''
            
    def _done_callback(self):
        self.text += '\n'
        
        
class Dialog_Box(gui.Container):
        
    defaults = {"callback" : tuple()}
    required_attributes = ("callback", )
    
    def __init__(self, **kwargs):
        super(Dialog_Box, self).__init__(**kwargs)
        self.create("pride.gui.widgetlibrary.Text_Box", text=self.text,
                    allow_text_edit=False, pack_mode="top")
        self.user_text = self.create("pride.gui.widgetlibrary.Prompt",
                                     use_done_button=True, pack_mode="bottom",
                                     h_range=(0, 80), callback=(self.reference, "handle_input"))
   
    def handle_input(self, user_input):
        reference, method = self.callback
        getattr(pride.objects[reference], method)(user_input)       
        
        
class Palette_Button(pride.gui.gui.Button):
    
    defaults = {"button_type" : ''}
    required_attributes = ("button_type", )
    
    def deselected(self, mouse, next_active_item):
        pride.objects[next_active_item].create(self.button_type)
        
        
class Palette(pride.gui.gui.Window):
    
    defaults = {"button_types" : tuple()}
    
    def __init__(self, **kwargs):
        super(Palette, self).__init__(**kwargs)
        for button_type in self.button_types:
            self.create(Palette_Button, button_type=button_type, pack_mode="top")
        