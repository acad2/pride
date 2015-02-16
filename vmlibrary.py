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

Instruction = base.Instruction
timer_function = utilities.timer_function

class Process(base.Base):
    """a base process for processes to subclass from. Processes are managed
    by the system. The start method begins a process while the run method contains
    the actual code to be executed every frame."""

    defaults = defaults.Process
    parser_ignore = ("auto_start", "network_buffer", "keyboard_input")

    def __init__(self, **kwargs):
        self.args = tuple()
        self.kwargs = dict()
        super(Process, self).__init__(**kwargs)

        run_instruction = self.run_instruction = Instruction(self.instance_name, "run")
        run_instruction.priority = self.priority
        run_instruction.log_processor_time = True

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


class Processor(base.Base):

    defaults = defaults.Processor

    def __init__(self, **kwargs):
        self.running = True
        super(Processor, self).__init__(**kwargs)
        
    def run(self):
        instructions = mpre.Instructions
        parallel_instructions = mpre.Parallel_Instructions
        Component_Resolve = base.Component_Resolve
        processor_name = self.instance_name
        
        sleep = time.sleep
        heappop = heapq.heappop
        _getattr = getattr        
        
        component_errors = (AttributeError, KeyError)
        reraise_exceptions = (SystemExit, KeyboardInterrupt)
        alert = self.alert
        component_alert = partial(alert, "{0}: {1} {2} does not exist", level=0)
        exception_alert = partial(alert, 
                                  "\nException encountered when processing {0}.{1}\n{2}", 
                                  level=0)
        
        format_traceback = traceback.format_exc
                
        while self.running:
            execute_at, instruction = heappop(instructions)            
            try:
                call = _getattr(Component_Resolve[instruction.component_name],
                                                  instruction.method)               
            except component_errors as error:                
                _type = (str(error).replace("Error", '') if 
                         type(error) == AttributeError else "component")
                                
                component_alert((instruction, instruction.component_name, _type)) 
                continue
                   
            alert("{0} executing code {1}", (processor_name, instruction), level="vvv")
            time_until = max(0, (execute_at - timer_function()))
            sleep(time_until)       
            try:
                call(*instruction.args, **instruction.kwargs)
            except BaseException as result:
                if type(result) in reraise_exceptions:
                    raise
                exception_alert((instruction.component_name,
                                 instruction.method,
                                 format_traceback()))
        
            if parallel_instructions:
                while parallel_instructions:
                    instance_name = parallel_instructions.pop(0)
                    Component_Resolve[instance_name].react()

            
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

        self.create("userinput.User_Input")

        for system_name, args, kwargs in self.system_configuration:
            system = self.create(system_name, *args, **kwargs)

    def run(self):
        processor = self.objects["Processor"][0]
        processor.run()