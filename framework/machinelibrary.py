#   mpf.machinelibrary - virtual machine - processor - event handler 
#
#    Copyright (C) 2014  Ella Rose
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pickle
import sys
import os
import atexit
import Queue
import time
from operator import attrgetter

import base
import defaults
Event = base.Event

try:
    from keyboard import Keyboard
except:
    raise
    import posixkeyboard
    Keyboard = posixkeyboard.Keyboard
    posixkeyboard.toggle_echo(sys.stdin.fileno(), False)
    atexit.register(posixkeyboard.toggle_echo, sys.stdin.fileno(), True)
 

class Timer(base.Base):
    
    defaults = defaults.Timer
    
    def __init__(self, wait_time, method, *args, **kwargs):
        try: # created via .create syntax
            self.parent = kwargs.pop("parent")
            self.parent_weakref = kwargs.pop("parent_weakref")
        except KeyError:
            pass
        super(Timer, self).__init__()
        self.wait_time = wait_time
        self.method = method
        self.target_time = time.time() + self.wait_time
        if not args:
            args = tuple()
        if not kwargs:
            kwargs = {}
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        if time.time() < self.target_time:
            return
        results = self.method(*self.args, **self.kwargs)
        self.target_time = time.time() + self.wait_time
        return results
  
  
class Task_Scheduler(base.Process):
    
    defaults = defaults.Task_Scheduler
    
    def __init__(self, **kwargs):
        super(Task_Scheduler, self).__init__(**kwargs)
        self.objects["Timer"] = []
                
    def run(self):
        for timer in self.objects["Timer"]:
            timer.run()
                
        if self in self.parent.objects[self.__class__.__name__]:
            Event("Task_Scheduler0", "run", component=self).post()

            
class Processor(base.Hardware_Device):
    
    defaults = defaults.Processor
    
    def __init__(self, **kwargs):
        self.execution_times = {}
        super(Processor, self).__init__(**kwargs)
        
    def run(self):
        self.events = sorted(getattr(Event_Handler, self._instance_name + "_queue"), key=attrgetter("priority"))
        setattr(Event_Handler, "%s_queue" % self._instance_name, [])
        #v: print "got events from %s_queue" % self._instance_name
        #v: print "processing events: ", [str(event) for event in self.events]
        for event in self.events:
            frequency = event.priority * .001
            #self.create(Timer, frequency,  getattr(
            #v: print "executing code", str(event)
            event.execute_code()
            #self.execution_times[(event.component_name, event.method)] = time.clock() - event.execute_at

            
class Event_Handler(base.Hardware_Device):
    """Dispatches events to Processors via pipes."""
    
    defaults = defaults.Event_Handler
    
    def __init__(self, **kwargs):
        self.processor_events = {}
        super(Event_Handler, self).__init__(**kwargs)
                           
    def run(self):
        #v: print self, "running"
        #self.get_frame_time()
        self.prepare_queue()   
        while not self.queue_empty:
            for processor_number in range(self.number_of_processors):
                event = self.get_event()
                if not event.component:
                    event.component = base.Component_Resolve[event.component_name]
                self.processor_events["Processor%s" % processor_number].append(event)
          
        for processor_number, event_list in self.processor_events.items():
            setattr(Event_Handler, "%s_queue" % processor_number, event_list)
            self.processor_events[processor_number] = []
            #v: print "Distributed %s events to %s" % (len(event_list), processor_number)
            #vv: print "\t" + [str(item) for item in event_list]          
        
        time.sleep(self.idle_time)
     
    def get_frame_time(self):
        old_time = self.frame_times.pop(self.frame_index)
        self.frame_times[self.frame_index] = new_time = time.time()
        
    def prepare_queue(self):        
        frame_queue = base.Event._get_events()
        event_list = []
        while not frame_queue.empty():
            event_list.append(frame_queue.get_nowait())
        self.frame_queue = sorted(event_list, key=attrgetter("priority"))
        self.queue_empty = False           
                
    def get_event(self):
        # returns a single event from the frame queue
        #v: print "getting event from frame queue", len(self.frame_queue)
        try:
            event = self.frame_queue.pop(0)
        except IndexError: 
            self.queue_empty = True
            #v: print "queue empty!"
            event = Event("Event_Handler0", "run", component=self, priority=0)
        return event
        
            
class Machine(base.Base):
    
    defaults = defaults.Machine
    
    def __init__(self, **kwargs):
        super(Machine, self).__init__(**kwargs)
  
        base.Component_Resolve["Machine"] = self
        self.event_handler = self.create(Event_Handler)
        self.status = "running"
        
        for processor_number in range(self.processor_count):
            self.event_handler.processor_events["Processor%s" % processor_number] = []
            self.create(Processor)
           
        for device_name, args, kwargs in self.hardware_configuration:
            hardware_device = self.create(device_name, *args, **kwargs)
            
        for system_name, args, kwargs in self.system_configuration:
            system = self.create(system_name, *args, **kwargs)             
        
    def create(self, *args, **kwargs):
        instance = super(Machine, self).create(*args, **kwargs)
        hardware_configuration = getattr(instance, "hardware_configuration", None)
        if hardware_configuration:
            for hardware_device in hardware_configuration:
                instance.add(self.objects[hardware_device.split(".")[1]][0])
        return instance
        
    def run(self):
        self.event_handler.run()
        while self.status:
            print "machine running"
            for processor in self.objects["Processor"]:
                processor.run()