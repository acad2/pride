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
import timeit
import pprint
from functools import partial

import pride
import pride.base

Instruction = pride.Instruction
timer_function = timeit.default_timer

class Process(pride.base.Base):
    """ usage: Process(target=function, args=..., kwargs=...) => process_object
    
        Create a virtual process. Note that while Process objects
        allow for the interface of target=function, the preferred usage
        is via subclassing.       
        
        The start method simply calls the run method, but can be overriden 
        if the entry point would be useful, and keeps a similar interface
        with the standard library threading/process model.
        
        Subclasses should overload the run method. Use of a process 
        object presumes the desire for some kind of explicitly timed
        or periodic event."""

    defaults = {"priority" : .04, "context_managed" : False, "running" : True,
                "run_callback" : None, "run_condition" : '', "_run_queued" : False}
    
    parser_ignore = ("priority", "run_callback", "context_managed", "_run_queued")
    
    verbosity = {"run_condition_false" : "vvv"}
    
    def __init__(self, **kwargs):
        self.args = tuple()
        self.kwargs = dict()
        super(Process, self).__init__(**kwargs)
        self.latency = resolve_string("pride.utilities.Latency")(self.instance_name)
        self.run_instruction = Instruction(self.instance_name, "_run")
        if self.running:
            Instruction(self.instance_name, "start").execute()

    def start(self):
        self.run_instruction.execute(priority=self.priority,
                                     callback=self.run_callback)
        self._run_queued = True
        
    def _run(self):
        if self.instance_name == "->Python->Network":
            self.latency.mark()
            pprint.pprint(self.latency.measurements)
        self._run_queued = False
        if self.context_managed:
            with self:
                result = self.run()
        else:
            result = self.run()
        if self.running:
            if self.run_condition and not getattr(self, self.run_condition):
                self.alert("Run condition False; Not running", 
                           level=self.verbosity["run_condition_false"])
            else:
                self.run_instruction.execute(priority=self.priority, 
                                             callback=self.run_callback)
                self._run_queued = True
        return result
        
    def run(self):
        if self.target:
            return self.target(*self.args, **self.kwargs)
                        
    def delete(self):
        self.running = False
        try:
            for entry in pride.Instruction.caller.pop(self.instance_name):
                pride.Instruction.instructions.remove(entry)
        except KeyError:
            pass
        pride.Instruction.instructions.sort()
        super(Process, self).delete()
        
    def __getstate__(self):
        attributes = super(Process, self).__getstate__()
        del attributes["run_instruction"]
        return attributes
        
    def on_load(self, state):
        super(Process, self).on_load(state)
        self.run_instruction = Instruction(self.instance_name, "_run")
        if self.running:
            Instruction(self.instance_name, "start").execute()
            
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        if traceback:
            raise
        return value
        
    
class Processor(Process):
    """ Removes enqueued Instructions via heapq.heappop, then
        performs the specified method call while handling the
        possibility of the specified component/method not existing,
        and any exception that could be raised inside the method call
        itself."""
        
    defaults = {"running" : False, "execution_verbosity" : 'vvvv',
                "parse_args" : True}

    parser_ignore = ("running", )
    parser_modifiers = {"exit_on_help" : False}
            
    verbosity = {"instruction_execution" : "instruction_execution", "component_alert" : 0,
                 "exception_alert" : 0}
    
    def run(self):
        self._return = {}
        instructions = pride.Instruction.instructions
        caller = pride.Instruction.caller
        #objects = pride.objects
                
        sleep = time.sleep
        heappop = heapq.heappop
        _getattr = getattr        
        
        component_errors = (AttributeError, KeyError)
        reraise_exceptions = (SystemExit, KeyboardInterrupt)
        alert = self.alert
        component_alert = partial(alert, "{0}:\n    {1}", level=self.verbosity["component_alert"])
        exception_alert = partial(alert, 
                                  "\nException encountered when processing {0}.{1}\n{2}", 
                                  level=self.verbosity["exception_alert"])
        execution_alert = partial(alert, "executing instruction {}")
        format_traceback = traceback.format_exc
               
        while instructions and self.running:            
            key = execute_at, instruction, callback = heappop(instructions)
            component_name = instruction.component_name
            caller[component_name].remove(key)                  
            try:
                call = _getattr(objects[component_name], instruction.method)
            except KeyError:
                error = "'{}' component does not exist".format(component_name)                        
                component_alert((str(instruction), error)) 
                continue
            except AttributeError as error:
                component_alert((str(instruction), error))
                continue
                
            time_until = max(0, (execute_at - timer_function()))
            if time_until:
                sleep(time_until)
                                
            execution_alert([instruction], level=self.verbosity["instruction_execution"])
            try:
                result = call(*instruction.args, **instruction.kwargs)
            except BaseException as result:
                if type(result) in reraise_exceptions:
                    raise
                else:
                    exception_alert((component_name, instruction.method, format_traceback()))
            else:
                if callback:
                    callback(result)