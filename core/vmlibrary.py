#   mpf.vmlibrary - virtual machine - processor - event handler 
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
from collections import deque
from operator import attrgetter

import base
import defaults
import utilities
from keyboard import Keyboard
from decoratorlibrary import Timed
Event = base.Event
 

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
        while True:
            self.events = sorted(getattr(Event_Handler, self.instance_name + "_queue"), key=attrgetter("priority"))
            setattr(Event_Handler, "%s_queue" % self.instance_name, [])
            #v: print "got events from %s_queue" % self.instance_name
            #v: print "processing events: ", [str(event) for event in self.events]
            for event in self.events:
                if not event.component:
                    event.component = base.Component_Resolve[event.component_name]
                #v: print "executing code", str(event)
                call = (event.component_name, event.method)
                time_taken, results = Timed(event.execute_code)()
                try:
                    self.execution_times[call].add(time_taken)
                except KeyError:
                    average = self.execution_times[call] = utilities.Average(name=call, size=5)
                    average.add(time_taken)
                #vv: print "%s takes about %ss to execute" % (call, self.execution_times[call].average)    
                    
class Event_Handler(base.Hardware_Device):
    """Dispatches events to Processors"""
    
    defaults = defaults.Event_Handler
    
    def __init__(self, **kwargs):
        self.processor_events = {}
        latency_options = {"name" : "%s frame time" % self.instance_name,
                           "average_size" : 5}
        self.frame_time = utilities.Latency(**latency_options)
        self.frame_queue = deque([[] for x in xrange(100)], 100)
        super(Event_Handler, self).__init__(**kwargs)
                           
    def run(self):
        #v: print self, "running"
        self.frame_time.update()
        #self.frame_time.display()
        self.prepare_queue()   
        while not self.queue_empty:
            for processor_number in range(self.number_of_processors):
                event = self.get_event()
                self.processor_events["Processor%s" % processor_number].append(event)
          
        for processor_number, event_list in self.processor_events.items():
            setattr(Event_Handler, "%s_queue" % processor_number, event_list)
            self.processor_events[processor_number] = []
            #v: print "Distributed %s events to %s" % (len(event_list), processor_number)
            #vv: print "\t" + [str(item) for item in event_list]    
        time.sleep(self.idle_time)
             
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
            event = Event("Event_Handler0", "run", component=self, priority=100)
        return event
        

class System(base.Base):
    """a class for managing components and applications.
    
    usually holds components such as the event handler, network manager, display,
    and so on. hotkeys set at the system level will be called if the key(s) are
    pressed and no other active object have the keypress defined."""
    
    defaults = defaults.System
    #hotkeys are specified in the form of keycode:Event pairs in a dictionary.
    # currently not implemented - awaiting pysdl
    hotkeys = {}
        
    def __init__(self, **kwargs):
        # sets default attributes
        super(System, self).__init__(**kwargs)
        
        #v: print "%s starting with %s" % (self.instance_name, self.startup_processes)
        for component, args, kwargs in self.startup_processes:
            #v: print "creating", component, args, kwargs
            self.create(component, *args, **kwargs)           
                    
    def exit(self):
        sys.exit()
             
    def run(self):
        pass

        
class Machine(base.Base):
    
    defaults = defaults.Machine
    
    def __init__(self, **kwargs):
        super(Machine, self).__init__(**kwargs)
        
        self.event_handler = self.create(Event_Handler)
                
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
        for processor in self.objects["Processor"]:
            processor.run()