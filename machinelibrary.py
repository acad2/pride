import pickle
import sys
import os
import atexit
import Queue
from operator import attrgetter

import base
import defaults
Event = base.Event
try:
    from windowskeyboard import Keyboard
except:
    import posixkeyboard
    Keyboard = posixkeyboard.Keyboard
    posixkeyboard.toggle_echo(sys.stdin.fileno(), False)
    atexit.register(posixkeyboard.toggle_echo, sys.stdin.fileno(), True)
 

class Processor(base.Hardware_Device):
    
    defaults = defaults.Processor
    
    def __init__(self, *args, **kwargs):
        super(Processor, self).__init__(*args, **kwargs)
        
    def run(self):
        #serialized_events = os.read(self.buffer, 8096)
        #events = pickle.loads(serialized_events)
        events = getattr(Event_Handler, self._instance_name + "_queue")
        setattr(Event_Handler, "%s_queue" % self._instance_name, [])
        #v: print "got events from %s_queue" % self._instance_name
        for event in events:
            #vv: print self._instance_name, "executing", event, event.args, event.kwargs
            event.execute_code()
            
            
class Event_Handler(base.Hardware_Device):
    """Dispatches events to Processors via pipes."""
    
    defaults = defaults.Event_Handler
    
    def __init__(self, *args, **kwargs):
        self.processor_events = {}
        super(Event_Handler, self).__init__(*args, **kwargs)
        self.thread = self._new_thread()
        
    def run(self):
        return next(self.thread)
        
    def _new_thread(self): # cannot be perpetuated by events  
        #v: print self, "running"
        while True:
            self.prepare_queue()       
            while not self.queue_empty:
                for processor_number in range(self.number_of_processors):
                    event = self.get_event()
                    if not event.component:
                        event.component = base.Component_Resolve[event.component_name]
                    self.processor_events["Processor%s" % processor_number].append(event)
            
            for processor_number, event_list in self.processor_events.items():
                setattr(Event_Handler, "%s_queue" % processor_number, sorted(event_list, key=attrgetter("priority")))
                self.processor_events[processor_number] = []
                #v: print "Distributed %s events to %s" % (len(event_list), processor_number)
                #vv: print "\t" + [str(item) for item in event_list]
                #serialized_events = pickle.dumps(event_list)
                #os.write(base.Components["Processor"+processor_number], serialized_events)                
            yield
            
    def prepare_queue(self):      
        self.frame_queue = base.Event._get_events()
        self.queue_empty = False           
                
    def get_event(self):
        # returns a single event from the frame queue
        try:
            event = self.frame_queue.get_nowait()
        except Queue.Empty: 
            self.queue_empty = True
            event = Event("Idle0", "run")
        return event
        
            
class Machine(base.Base):
    
    defaults = defaults.Machine
    
    def __init__(self, *args, **kwargs):
        super(Machine, self).__init__(*args, **kwargs)
  
        base.Component_Resolve["Machine"] = self
        self.event_handler = self.create(Event_Handler)
        
        for processor_number in range(self.processor_count):
            self.event_handler.processor_events["Processor%s" % processor_number] = []
            self.create(Processor)
           
        for device_name, args, kwargs in self.hardware_configuration:
            hardware_device = self.create(device_name, *args, **kwargs)
            
        for system_name, args, kwargs in self.system_configuration:
            system = self.create(system_name, *args, **kwargs)
            for hardware_device in system.hardware_configuration:
                system.add(self.objects[hardware_device.split(".")[1]][0])                
        self.thread = self._run()
        
    def run(self):
        while True:
            #vv: print "nexting machine thread"
            next(self.thread)
        
    def _run(self):
        while True:
            #vv: print "processing frame"
            self.event_handler.run()
            for processor in self.objects["Processor"]:
                processor.run()
            yield