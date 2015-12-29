""" Stores global objects including instructions and the environment """
import sys
import pride.preprocessing
        
compiler = pride.preprocessing.Compiler(preprocessors=(pride.preprocessing.Preprocess_Decorator, ),
                                        modify_builtins=None)                                    

import heapq
import inspect
import mmap
import itertools
import pprint
import pickle
import contextlib
import copy
import types
import timeit
timer_function = timeit.default_timer
    
def preprocess(function):
    raise ImportError("Failed to replace preprocess function with source")     
         

class Instruction(object):
    """ usage: Instruction(component_name, method_name,
                           *args, **kwargs).execute(priority=priority,
                                                    callback=callback)

            - component_name is the string instance_name of the component
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.


        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will be performed. Instructions are useful for explicitly
        timed/recurring tasks.

        Instructions may be reused. The same instruction object can be
        executed any number of times.

        Note that Instructions must be executed to have any effect, and
        that they do not happen inline even if the priority is 0.0. In
        order to access the result of the executed function, a callback
        function can be provided."""

    caller = {}
    instructions = []
    
    def __init__(self, component_name, method, *args, **kwargs):
        super(Instruction, self).__init__()
        self.created_at = timer_function()
        self.component_name = component_name
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def execute(self, priority=0.0, callback=None):
        """ usage: instruction.execute(priority=0.0, callback=None)

            Submits an instruction to the processing queue.
            The instruction will be executed in priority seconds.
            An optional callback function can be provided if the return value
            of the instruction is needed. """
        key = (timer_function() + priority, self, callback)
        try:
            self.caller[self.component_name].append(key)
        except KeyError:
            self.caller[self.component_name] = [key]
        heapq.heappush(self.instructions, key)

    def __str__(self):
        return "Instruction({}.{}, {}, {})".format(self.component_name, self.method,
                                                   self.args, self.kwargs)

_last_creator = ''
# compatibility purposes
objects = objects

# Things must be done in this order for Alert_Handler to exist inside this file
# and reuse Base machinery, namely for argument parsing. 
import pride.base

class Alert_Handler(pride.base.Base):
    """ Provides the backend for the base.alert method. The print_level
        and log_level attributes act as global levels for alerts;
        print_level and log_level may be specified as command line arguments
        upon program startup to globally control verbosity/logging. """
    level_map = {0 : 'alert ',
                '' : "stdout ",
                'v' : "notification ",
                'vv' : "verbose notification ",
                'vvv' : "very verbose notification ",
                'vvvv' : "extremely verbose notification "}

    defaults = {"log_level" : '0+v', "print_level" : '0',
                "log_name" : "Alerts.log", "log_is_persistent" : False,
                "parse_args" : True}

    parser_ignore = ("parse_args", "log_is_persistent", "verbosity")
    parser_modifiers = {"exit_on_help" : False}
    
    def _get_print_level(self):
        return self._print_level
    def _set_print_level(self, value):
        value = value or '0'
        print_level = value.split('+')
        if '0' in print_level:
            print_level.remove('0')
            print_level.append(0)
        self._print_level = print_level
    print_level = property(_get_print_level, _set_print_level)

    def _get_log_level(self):
        return self._log_level
    def _set_log_level(self, value):
        value = value or '0'
        log_level = value.split('+')
        if '0' in log_level:
            log_level.remove('0')
            log_level.append(0)
        self._log_level = log_level
    log_level = property(_get_log_level, _set_log_level)
        
    def __init__(self, **kwargs):
        super(Alert_Handler, self).__init__(**kwargs)
        self.log = open(self.log_name, 'a+')

alert_handler = Alert_Handler()

class Finalizer(base.Base):
    
    mutable_defaults = {"_callbacks" : list}
        
    def run(self):
        for callback, args, kwargs in self._callbacks:
            try:
                instance_name, method = callback
            except ValueError:
                pass
            else:
                try:
                    callback = getattr(objects[instance_name], method)
                except KeyError:
                    self.alert("Unable to load object for callback: '{}'".format(instance_name), level=0)
                except AttributeError:
                    self.alert("Unable to call method: '{}.{}'".format(instance_name, method), level=0)
            try:
                callback(*args, **kwargs)
            except Exception as error:
                self.alert("Unhandled exception running finalizer method '{}.{}'\n{}",
                           (instance_name, method, error), level=0)
        compiler.database.close()
        self._callbacks = []    
        
    def add_callback(self, callback, *args, **kwargs):
        self._callbacks.append((callback, args, kwargs))
        
    def remove_callback(self, callback, *args, **kwargs):
        self._callbacks.remove((callback, args, kwargs))
        
finalizer = Finalizer()        

import pride.patch
for name in pride.patch.patches:
    getattr(pride.patch, name)()