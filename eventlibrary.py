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
        
   
class Timer(base.Base):
    
    
    def __init__(self, wait_time, method, *args, **kwargs):
        self.parent = kwargs.pop("parent")
        self.parent_weakref = kwargs.pop("parent_weakref")
        super(Timer, self).__init__(wait_time=wait_time, method=method,
        args=args, kwargs=kwargs)
        self.parent.threads[self] = self.new_thread()
        self.recurring = True
        _time = time.time()
        self.target_time = _time+self.wait_time
                
        if not hasattr(self, "args"):
            self.args = tuple()
        if not hasattr(self, "kwargs"):
            self.kwargs = {}
            
    def new_thread(self):
        while time.time() <= self.target_time:
            yield
        self.method(*self.args, **self.kwargs)
        if self.recurring:
            self.parent.threads[self] = self.new_thread()
            self.target_time = time.time()+self.wait_time
        yield
        
        
class Task_Scheduler(base.Process):
    
    defaults = defaults.Task_Scheduler
    
    def __init__(self, *args, **kwargs):
        super(Task_Scheduler, self).__init__(*args, **kwargs)
        self.threads = {}
                
    def run(self):
        for thread in self.threads.values():
            next(thread)
                
        if self in self.parent.objects[self.__class__.__name__]:
            Event("Task_Scheduler0", "run").post()
            
#def 