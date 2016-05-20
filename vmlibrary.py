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
import itertools
from functools import partial

import pride
import pride.base

Instruction = pride.Instruction
timestamp = timeit.default_timer
        
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
    
    parser_ignore = ("priority", "run_callback", "context_managed", "_run_queued", "run_condition")
    
    verbosity = {"run_condition_false" : "vvv"}
    
    def __init__(self, **kwargs):
        self.args = tuple()
        self.kwargs = dict()
        super(Process, self).__init__(**kwargs)        
        self.run_instruction = Instruction(self.reference, "_run")
        
        if self.running:
            Instruction(self.reference, "start").execute()

    def start(self):
        self.run_instruction.execute(priority=self.priority,
                                     callback=self.run_callback)
        self._run_queued = True
        
    def _run(self):
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
        pride.Instruction.purge(self.reference)
        super(Process, self).delete()
        
    def __getstate__(self):
        attributes = super(Process, self).__getstate__()
        del attributes["run_instruction"]
        return attributes
        
    def on_load(self, state):
        super(Process, self).on_load(state)
        self.run_instruction = Instruction(self.reference, "_run")
        if self.running:
            Instruction(self.reference, "start").execute()
            
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
                 "exception_alert" : 0, "callback_exception" : 0}
    
    def run(self):
        self._return = {}
        instructions = pride.Instruction.instructions        
                        
        sleep = time.sleep
        heappop = heapq.heappop
        _getattr = getattr        
        
        component_errors = (AttributeError, KeyError)
        reraise_exceptions = (SystemExit, KeyboardInterrupt)
        alert = self.alert
        verbosity = self.verbosity
        component_alert = partial(alert, "{0}:\n    {1}", level=verbosity["component_alert"])
        exception_alert = partial(alert, 
                                  "\nException encountered when processing {0}.{1}\n{2}", 
                                  level=verbosity["exception_alert"])
        execution_alert = partial(alert, "executing instruction {}")
        callback_exception_alert = partial(alert, "Exception in callback '{}'", level=verbosity["callback_exception"])
        format_traceback = traceback.format_exc
        result = null_result = [] # a unique object
        while instructions and self.running:   
            try:
                while True:                    
                    (execute_at, instruction, callback, 
                     component_name, method, args, kwargs,
                     execute_flag) = heappop(instructions)
                     
                    if execute_flag:
                        call = _getattr(objects[component_name], method)
                            
                        time_until = max(0, (execute_at - timestamp()))
                        if time_until:
                            sleep(time_until)
                                            
                        execution_alert([instruction], level=verbosity["instruction_execution"])
                        
                        if callback:
                            result = call(*args, **kwargs)
                            callback(result)
                            result = null_result
                        else:
                            call(*args, **kwargs)                        
            except KeyError:                 
                if component_name in objects:
                    if callback:
                        if result is not null_result:
                            callback_exception_alert((callback, ))
                            continue
                    exception_alert((component_name, method, format_traceback()))
                else:
                    error = "'{}' component does not exist".format(component_name)                        
                    component_alert((str(instruction), error)) 
                    
            except AttributeError as error:                
                if hasattr(objects[component_name], method):
                    if callback and result is not null_result:
                        callback_exception_alert((callback, ))
                    else:
                        exception_alert((component_name, method, format_traceback()))
                else:
                    component_alert((str(instruction), error))   
                    
            except BaseException as error:                   
                if type(error) in reraise_exceptions:                                        
                    raise
                else:                                        
                    if callback and result is not null_result:
                        callback_exception_alert((callback, ))
                    else:
                        exception_alert((component_name, method, format_traceback()))
               

class Idle_Process(Process):
    
    defaults = {"priority" : 300.0}
    
    def run(self):
        for reference, method_name in itertools.ichain(self.callbacks, self.single_callbacks):
            getattr(pride.objects[reference], method_name)()
        del self.single_callbacks[:]
        
    def register_callback(self, reference, method_name, single_use=False):
        if single_use:
            self.single_callbacks.append((reference, method_name))
        else:
            self.callbacks.append((reference, method_name))
            
                    