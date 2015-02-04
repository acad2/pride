#   mpf.vmlibrary - virtual machine - processor - instruction handler
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
import dis
from cStringIO import StringIO
from collections import deque
from operator import attrgetter
from functools import partial

import mpre
import base
import defaults
import utilities
from stdin import Stdin

Instruction = base.Instruction
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
        if self.network_packet_size:
            self.network_buffer = {}
        run_instruction = self.run_instruction = Instruction(self.instance_name, "run")
        run_instruction.priority = self.priority
        run_instruction.log_processor_time = True
        Instruction("Processor", "cache_instruction", run_instruction, self.run).execute()
        if self.auto_start:
            self.process("start")

    def process(self, method_name, *args, **kwargs):
        instruction = Instruction(self.instance_name, method_name, *args, **kwargs)
        instruction.priority = self.priority
        instruction.execute()

    def start(self): # (hopeful) compatibility with multiprocessing.Process
        self.run()

    def run(self):
        if self.target:
            self.target(*self.args, **self.kwargs)

        self.run_instruction.execute()
            

class Thread(base.Base):
    """does not run in parallel like threading.thread"""
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
        self.instruction_cache = {}
        self.running = True
        super(Processor, self).__init__(**kwargs)
        
    def cache_instruction(self, instruction, method):
        self.instruction_cache[instruction] = method        

    def uncache(self, instruction):
        del self.instruction_cache[instruction]
        
    def run(self):
        instructions = mpre.Instructions
        Component_Resolve = base.Component_Resolve
        processor_name = self.instance_name
        log_time = self.log_time

        sleep = time.sleep
        heappop = heapq.heappop
        get_attribute = getattr

        cache = self.instruction_cache
        
        component_errors = (AttributeError, KeyError)
        reraise_exceptions = (SystemExit, KeyboardInterrupt)#, StopIteration)
        alert = self.alert
        component_alert = partial(alert, "{0}: {1} {2}", level=0)
        exception_alert = partial(alert, "\nException encountered when processing {0}.{1}\n{2}", level=0)
        
        format_traceback = traceback.format_exc
                
        while self.running:
            execute_at, instruction = heappop(instructions)            
            try:
                component = Component_Resolve[instruction.component_name]
                call = cache[instruction] if instruction in cache else\
                       getattr(component, instruction.method)
                       
            except component_errors as error:                
                _type = str(error).replace("Error", '') if type(error) == AttributeError\
                        else "component"
                
                component_name = instruction.component_name
                component_alert((instruction, instruction.component_name, _type)) 
                continue
                   
            alert("{0} executing code {1}", (processor_name, instruction), level="vvv")
            time_until = max(0, (execute_at - timer_function()))
            sleep(time_until)       
            try:
                start = timer_function()
                call(*instruction.args, **instruction.kwargs)
                ended_at = timer_function()
            except BaseException as result:
                if type(result) in reraise_exceptions:
                    raise
                exception_alert((instruction.component_name,
                                 instruction.method,
                                 format_traceback()))

            if instruction.log_processor_time:
                log_time(ended_at - start, str(instruction))
             
    def log_time(self, time_taken, call):
        try:
            self.execution_times[call].add(time_taken)
        except KeyError:
            average = self.execution_times[call] = utilities.Average(name=call, size=10)
            average.add(time_taken)

    def display_processor_usage(self):
        print "\n{: <40} {:>}".format("Process name", "Average running time")
        for process, time_taken in self.execution_times.iteritems():
            print "{: <40} {:>}".format(process[11:], time_taken.meta_average)
        

class System(base.Base):
    """a class for managing components and applications.

    usually holds components such as the instruction handler, network manager, display,
    and so on. hotkeys set at the system level will be called if the key(s) are
    pressed and no other active object have the keypress defined."""

    defaults = defaults.System
    #hotkeys are specified in the form of keycode:Instruction pairs in a dictionary.
    # currently not implemented - awaiting pysdl
    hotkeys = {}

    def __init__(self, **kwargs):
        # sets default attributes
        super(System, self).__init__(**kwargs)

        self.alert("{0} starting with {1}", (self.instance_name, str(self.startup_processes)), "v")
        for component, args, kwargs in self.startup_processes:
            self.alert("creating {0} with {1} {2}", (component, args, kwargs), "vv")
            self.create(component, *args, **kwargs)

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