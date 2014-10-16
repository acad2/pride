import sys
import os
import multiprocessing
import time
from operator import attrgetter
import Queue as que
Queue = que.Queue
from weakref import proxy
import base
import functionlibrary
import defaults                            
 
Event = base.Event

class Task(base.Base):
    
    defaults = defaults.Base
    
    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        
   
                  
            
class Task_Scheduler(base.Process):
    
    defaults = defaults.Task_Scheduler
    
    def __init__(self, *args, **kwargs):
        super(Task_Scheduler, self).__init__(*args, **kwargs)
        self.objects["Timer"] = []
                
    def run(self):
        for timer in self.objects["Timer"]:
            timer.run()
                
        if self in self.parent.objects[self.__class__.__name__]:
            Event("Task_Scheduler0", "run").post()
            
#def 