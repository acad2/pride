import sys
import multiprocessing
import time
from operator import attrgetter
import Queue as que
Queue = que.Queue
from weakref import proxy
import base
import functionlibrary
import defaults

              
class Event(object):

    def __init__(self, component_name, method, *args, **kwargs):
        super(Event, self).__init__()
        self.component_name = component_name
        self.method = method # any method can be supplied
        self.args = args # any arguments can be supplied
        self.kwargs = kwargs # any keyword arguments can be supplied
            
    def post(self):
        Event_Handler.events.put(self)
        
    def __str__(self):
        return "%s_Event: %s" % (self.component_name, self.method)
        
    def execute_code(self, component):
        call = getattr(component, self.method)
        call(*self.args, **self.kwargs)   


class Event_Handler(base.Process):

    events = Queue()
    defaults = defaults.Event_Handler
    
    def __init__(self, *args, **kwargs):
        super(Event_Handler, self).__init__(*args, **kwargs)
        self.thread = self.run()
        
    def run(self): # cannot be powered by events
        while True:
            self.prepare_queue()
            while not self.queue_empty:
                event = self.get_event()
                component = self.parent.objects[event.component_name][0]
                event.execute_code(component)
            yield               
            
    def prepare_queue(self):
        self.frame_queue = Event_Handler.events
        self.queue_empty = False
        Event_Handler.events = Queue()        
                
    def get_event(self):
        # returns a single event from the frame queue
        try:
            event = self.frame_queue.get_nowait()
        except que.Empty: 
            self.queue_empty = True
            event = Event("Idle", "run")
        return event
                             
 
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
            Event("Task_Scheduler", "run").post()
            
#def 