import time

import guilibrary
import defaults
from base import Event

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
        updater = Event(instance_name, "update_time")
        updater.priority = 1
        updater.component = self
        updater.post()
        Event(instance_name, "draw_texture").post()
