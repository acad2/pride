import time

import guilibrary
import defaults
from base import Instruction


class Popup_Menu(guilibrary.Container):

    defaults = defaults.Popup_Menu

    def __init__(self, **kwargs):
        super(Popup_Menu, self).__init__(**kwargs)
        Instruction("User_Input", "add_popup", self).execute()


class Homescreen(guilibrary.Window):

    defaults = defaults.Homescreen

    def __init__(self, **kwargs):
        super(Homescreen, self).__init__(**kwargs)
        self.create(Task_Bar)


class Task_Bar(guilibrary.Container):

    defaults = defaults.Task_Bar

    def __init__(self, **kwargs):
        super(Task_Bar, self).__init__(**kwargs)
        self.create(Date_Time_Button)


class Date_Time_Button(guilibrary.Button):

    defaults = defaults.Date_Time_Button

    def __init__(self, **kwargs):
        super(Date_Time_Button, self).__init__(**kwargs)
        self.update_time()

    def update_time(self):
        self.text = time.asctime()
        instance_name = self.instance_name
        updater = Instruction(instance_name, "update_time")
        updater.priority = 1
        updater.component = self
        updater.execute()
        Instruction(instance_name, "draw_texture").execute()


class Right_Click_Menu(Popup_Menu):

    defaults = defaults.Right_Click_Menu

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


class Right_Click_Button(guilibrary.Button):

    defaults = defaults.Right_Click_Button

    def __init__(self, **kwargs):
        super(Right_Click_Button, self).__init__(**kwargs)

    def click(self, mouse):
        self.create(Attribute_Displayer, attributes=self.attributes)


class Attribute_Displayer(guilibrary.Window): pass
