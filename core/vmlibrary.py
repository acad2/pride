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
from collections import deque
from operator import attrgetter
#import multiprocessing
import base
import defaults
import utilities
from keyboard import Keyboard
from decoratorlibrary import Timed
Event = base.Event
 
timer_function = utilities.timer_function
                        
                        
class Processor(base.Hardware_Device):
    
    defaults = defaults.Processor
    
    def __init__(self, **kwargs):
        self.execution_times = {}
        super(Processor, self).__init__(**kwargs)
        
    def run(self):
        events = Event.events
        Component_Resolve = base.Component_Resolve
        while True:
            execute_at, event = heapq.heappop(events)
            component_name = event.component_name
            if not event.component:
                try:
                    event.component = Component_Resolve[component_name]
                except KeyError:
                    self.alert("{0} {1} component does not exist".format(event,
                    component_name), 5)  
                    continue
                    
            self.alert("{0} executing code ".format(self.instance_name) + str(event), 0)
            time_until = max(0, (execute_at - timer_function()))
            time.sleep(time_until)
            try:
                start = timer_function()
                results = event.execute_code()
            except BaseException as exception:
                if type(exception) in (SystemExit, KeyboardInterrupt):
                    raise
                print exception.traceback
            
            time_taken = timer_function() - start
            call = (component_name, event.method)
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
        
        self.alert("{0} starting with ".format(self.instance_name) + str(self.startup_processes), 2)
        for component, args, kwargs in self.startup_processes:
            self.alert("creating {0} with {1} {2}".format(component, args, kwargs), 1)
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
        #pool = multiprocessing.Pool()
        #while True:
        #   pool.map(processor.run, Event.events)