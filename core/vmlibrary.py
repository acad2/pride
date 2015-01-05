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
import heapq
import time
import traceback
from cStringIO import StringIO
from collections import deque
from operator import attrgetter

import base
import defaults
import utilities
from stdin import Stdin
from decoratorlibrary import Timed
Event = base.Event
 
timer_function = utilities.timer_function
stdin = Stdin() 
        
class Process(base.Base):
    """a base process for processes to subclass from. Processes are managed
    by the system. The start method begins a process while the run method contains
    the actual code to be executed every frame."""
    
    defaults = defaults.Process
    parser_ignore = ("auto_start", "network_buffer", "keyboard_input", "stdin_buffer_size")

    def __init__(self, **kwargs):
        self.args = tuple()
        self.kwargs = dict()
        super(Process, self).__init__(**kwargs)
            
        if self.auto_start:
            self.process("start")
            
    def process(self, method_name, *args, **kwargs):
        event = Event(self.instance_name, method_name, *args, **kwargs)
        event.priority = self.priority
        event.component = self
        event.post()
        
    def start(self): # (hopeful) compatibility with multiprocessing.Process
        self.run()
        
    def run(self):
        if self.target:
            self.target(*self.args, **self.kwargs)

        self.propagate()
 
    def adjust_priority(self):
        scaling_value = getattr(self, self.priority_scales_with, self.priority)
        scale_against = self.scale_against
        scale_function = getattr(scale_against, "__{0}__".format(self.scale_operator))
        priority = scale_function(scaling_value)
        #print self, "calculated priority", priority, scale_against, scaling_value
        priority = min(priority, self.minimum_priority)
        #print "after comparison to minimum", priority
        self.priority = max(priority, self.maximum_priority)
        #print "set priority to", self.priority
        args = (self.__class__.__name__, "adjust_priority")
        options = {"component" : self,
                   "priority" : self.update_priority_interval}
        self.alert("set {0} priority to {1}", (self, self.priority), 0)
        Event(*args, **options).post()
        
    def propagate(self):
        if self in self.parent.objects[self.__class__.__name__]:
            self.process("run")
        
        
class Thread(base.Base):
    """does not run in psuedo-parallel like threading.thread"""
    defaults = defaults.Thread 
                
    def __init__(self, **kwargs):
        self.args = tuple()
        self.kwargs = dict()
        self.results = []
        super(Thread, self).__init__(**kwargs)
                
    def start(self):
        self.run()
    
    def run(self): 
        return self.function(*self.args, **self.kwargs)

    
class Hardware_Device(base.Base):
    
    defaults = defaults.Hardware_Device
    
    def __init__(self, **kwargs):
        super(Hardware_Device, self).__init__(**kwargs)

        
class Processor(Hardware_Device):
    
    defaults = defaults.Processor
    
    def __init__(self, **kwargs):
        self.execution_times = {}
        super(Processor, self).__init__(**kwargs)
        
    def run(self):
        events = Event.events
        Component_Resolve = base.Component_Resolve
        processor_name = self.instance_name
        log_time = self.log_time
        alert = self.alert
        sleep = time.sleep
        
        while True:
            execute_at, event = heapq.heappop(events)
            component_name = event.component_name
            if not event.component:
                try:
                    event.component = Component_Resolve[component_name]
                except KeyError:
                    alert("{0}: {1} component does not exist", 
                              (event, component_name), 0)
                   # print Component_Resolve.keys()
                    continue

            alert("{0} executing code {1}", (processor_name, event), "vvv")
            time_until = max(0, (execute_at - timer_function()))
            sleep(time_until)
            try:
                start = timer_function()
                results = event.execute_code()
            except BaseException as exception:
                if type(exception) in (SystemExit, KeyboardInterrupt):
                    raise
                print getattr(exception, "traceback", traceback.format_exc())
            
            if event.log_processor_time:
                log_time(start, (component_name, event.method))
                
    def log_time(self, start, call):
        time_taken = timer_function() - start
        try:
            self.execution_times[call].add(time_taken)
        except KeyError:
            average = self.execution_times[call] = utilities.Average(name=call, size=5)
            average.add(time_taken)
                    
    def display_process_info(self):
        for process, time_taken in self.execution_times.iteritems():
            print process, time_taken.meta_average
            

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
        
        self.alert("{0} starting with {1}", (self.instance_name, str(self.startup_processes)), "v")
        for component, args, kwargs in self.startup_processes:
            self.alert("creating {0} with {1} {2}", (component, args, kwargs), "vv")
            self.create(component, *args, **kwargs)           
                    
    def exit(self):
        sys.exit()
             
    def run(self):
        pass

            
class Machine(base.Base):
    
    defaults = defaults.Machine
    
    def __init__(self, **kwargs):
        super(Machine, self).__init__(**kwargs)

        for processor_number in range(self.processor_count):
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
        processor = self.objects["Processor"][0]
        processor.run()