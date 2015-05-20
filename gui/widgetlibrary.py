import time

import mpre
import mpre.gui.gui as gui
import mpre.gui
import mpre.base as base
Instruction = mpre.Instruction


class Indicator(gui.Button):  
        
    def draw_texture(self):
        super(Indicator, self).draw_texture()
        parent = self.parent
        x, y, w, h = parent.area

        area = self.area = (self.x, self.y, len(self.parent.instance_name) * 7, 16)
        # draw a line from the top left corner of self to the midpoint of parent
        self.draw("line", (self.x, self.y, x + (w / 2), y + (h / 2)), color=self.outline_color)
        self.draw("text", parent.instance_name, area, color=(255, 255, 255))
                               
        
class Popup_Menu(gui.Container):

    defaults = gui.Container.defaults.copy()
    defaults.update({"popup" : True,
                     "pack_modifier" : (lambda parent, child: 
                                        setattr(child, "position", 
                                               (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2)))
                    })

    def __init__(self, **kwargs):
        super(Popup_Menu, self).__init__(**kwargs)
        Instruction("User_Input", "add_popup", self).execute()


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
        self.create(Date_Time_Button)
        
        
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


class Right_Click_Menu(Popup_Menu):

    defaults = Popup_Menu.defaults.copy()
    defaults.update({"pack_mode": "z",
                     "size" : (200, 150)})


    def __init__(self, **kwargs):
        super(Right_Click_Menu, self).__init__(**kwargs)
        types = ("builtins", "private", "methods", "properties", "attributes")
        attributes = dict((name, []) for name in types)
        target = self.target
        for attribute in dir(target):
            if "__" in attribute:
                attributes["builtins"].append(attribute)
            elif "_" == attribute[0]:
                attributes["private"].append(attribute)
            elif callable(getattr(target, attribute)):
                attributes["methods"].append(attribute)
            elif type(getattr(target, attribute)) is property:
                attributes["properties"].append(attribute)
            else:
                attributes["attributes"].append(attribute)
        for name, collection in attributes.items():
            self.create(Right_Click_Button, text=name, attributes=collection, size=(50, 50))
