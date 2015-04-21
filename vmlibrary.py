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
import heapq
import time
import traceback
from functools import partial

import mpre
import mpre.base as base
import mpre.defaults as defaults
import mpre.utilities as utilities

Instruction = mpre.Instruction
timer_function = utilities.timer_function

class Process(base.Reactor):
    """ usage: Process(target=function, args=..., kwargs=...) => process_object
    
        Create a logical process. Note that while Process objects
        allow for the interface of target=function, the preferred usage
        is via subclassing.
        
        Process objects have a run_instruction attribute. This attribute
        is a saved instruction: Instruction(self.instance_name, 'run'). 
        
        Process objects have a default attribute 'auto_start', which
        defaults to True. When True, an instruction for process.start
        will automatically be executed inside __init__.
        
        The start method simply calls the run method, but can be overriden 
        if the entry point would be useful, and keeps a similar interface
        with the standard library threading/process model.
        
        Subclasses should overload the run method. A process may propagate
        itself by executing a run instruction inside it's run method. While
        processes support the reaction interface, use of a process presumes
        the desire for some kind of explicitly timed Instruction. Examples
        of processes include polling for user input or socket buffers
        at various intervals.
        
        Some people may find the serial style, one frame at a time method
        offered by processes easier to understand and follow then reactions.
        Most things can be accomplished by either, though processes may be
        less performant then parallel_methods/reactions"""

    defaults = defaults.Process
    parser_ignore = ("auto_start", "network_buffer", "keyboard_input")

    def __init__(self, **kwargs):
        self.args = tuple()
        self.kwargs = dict()
        super(Process, self).__init__(**kwargs)

        run_instruction = self.run_instruction = Instruction(self.instance_name, "run")

        if self.auto_start:
            Instruction(self.instance_name, "start").execute()

    def start(self):
        self.run()

    def run(self):
        if self.target:
            self.target(*self.args, **self.kwargs)
            

class Processor(Process):
    """ Removes enqueued Instructions via heapq.heappop, then
        performs the specified method call while handling the
        possibility of the specified component/method not existing,
        and any exception that could be raised inside the method call
        itself."""
        
    defaults = defaults.Processor

    def __init__(self, **kwargs):
        self.running = True
        super(Processor, self).__init__(**kwargs)
        
    def run(self):
        instructions = self.environment.Instructions
        Component_Resolve = self.environment.Component_Resolve
        processor_name = self.instance_name
        
        sleep = time.sleep
        heappop = heapq.heappop
        _getattr = getattr        
        
        component_errors = (AttributeError, KeyError)
        reraise_exceptions = (SystemExit, KeyboardInterrupt)
        alert = self.alert
        component_alert = partial(alert, "{0}: {1}", level=0)
        exception_alert = partial(alert, 
                                  "\nException encountered when processing {0}.{1}\n{2}", 
                                  level=0)
        execution_alert = partial(alert, "executing instruction {}", level="vvv")
        format_traceback = traceback.format_exc
               
        while instructions and self.running:            
            execute_at, instruction, callback = heappop(instructions)           
            try:
                call = _getattr(Component_Resolve[instruction.component_name],
                                                  instruction.method)               
            except component_errors as error:
                if isinstance(error, KeyError):
                    error = "'{}' component does not exist".format(instruction.component_name)
                component_alert((str(instruction), error)) 
                continue
                   
            time_until = max(0, (execute_at - timer_function()))
            if time_until:
                sleep(time_until)
                
            execution_alert([str(instruction)])
            
            try:
                result = call(*instruction.args, **instruction.kwargs)
            except BaseException as result:
                if type(result) in reraise_exceptions:
                    raise
                exception_alert((instruction.component_name,
                                 instruction.method,
                                 format_traceback()))
            else:
                if callback:
                    callback(result)        