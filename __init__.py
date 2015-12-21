""" Stores global objects including instructions and the environment """
import sys
import pride.importers
compiler = pride.importers.Compiler(preprocessors=(importers.Preprocess_Decorator(),),
                                    modify_builtins=None)                                    
sys.meta_path.insert(0, compiler)

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
    
class Environment(object):
    """ Stores global state for the process. This includes reference
        reference information, most importantly the objects dictionary. """
    fields = ("objects", "instance_count", "instance_name",
              "instance_count", "parents", "references_to", "creation_count")

    def __init__(self):
        super(Environment, self).__init__()
        self.last_creator = None
        self.Instructions = []
        for field in self.fields:
            setattr(self, field, {})

    def display(self):
        """ Pretty prints environment attributes """
        print "\nInstructions: {}".format([(instruction[0],
                                            str(instruction[1])) for
                                           instruction in self.Instructions])

        for attribute in self.fields:
            print "\n" + attribute
            pprint.pprint(getattr(self, attribute))

    def replace(self, component, new_component):
        """ Replaces the instance component with the specified new_component.
            The new_component will be obtain the replaced components
            instance_name reference. The old component should be garbage
            collected. """
        if isinstance(component, unicode) or isinstance(component, str):
            component = self.objects[component]

        old_component_name = component.instance_name

        self.objects[old_component_name] = self.objects.pop(new_component.instance_name, 
                                                            new_component)

        self.instance_name[new_component] = self.instance_name.pop(component)
        
        parents = self.parents
        if component in parents:
            parents[new_component] = parents.pop(component)

        new_component.instance_name = old_component_name
        references = self.references_to.get(old_component_name, set()).copy()

        for referrer in references:
            instance = self.objects[referrer]
            instance.remove(component)
            instance.add(new_component)

    def delete(self, instance):
        """ Deletes an object from the environment. This is called by
            instance.delete. """
        try:
            objects = instance.objects
        except AttributeError: # non base objects have no .objects dictionary
            instance_name = self.instance_name[instance]
            parent = self.objects[self.parents[instance]]
            parent.objects[instance.__class__.__name__].remove(instance)
        else:
            instance_name = instance.instance_name
            if objects:
                for children in objects.values():
                    [child.delete() for child in list(children)]

        if instance in self.parents:
            del self.parents[instance]

        if instance_name in self.references_to:
            for referrer in list(self.references_to[instance_name]):
                self.objects[referrer].remove(instance)
            del self.references_to[instance_name]
        del self.objects[instance_name]
        del self.instance_name[instance]
        
    def register(self, instance):
        """ Registers an instance_name reference with the supplied instance. """
        instance_type = instance.__class__.__name__
        if not self.last_creator: # instance was not create'd
            try:
                count = self.instance_count[instance_type]
            except KeyError:
                count = self.instance_count[instance_type] = 0
            finally:
                self.instance_count[instance_type] += 1
                instance_name = "->" + instance_type + (str(count) if count else '')
        else:            
            parent_name = self.last_creator
            parent = self.objects[parent_name]
            try:
                count = self.creation_count[parent_name][instance_type]
            except KeyError: # instance_type not created yet
                try:
                    count = self.creation_count[parent_name][instance_type] = 0
                except KeyError: # parent_name has not created anything yet
                    self.creation_count[parent_name] = {instance_type : 0}
                    count = 0
            
            self.creation_count[parent_name][instance_type] += 1
            instance_name = (parent_name + "->" + instance_type + 
                            (str(count) if count else ''))
        try:
            self.instance_name[instance] = instance.instance_name = instance_name
        except AttributeError:
            self.instance_name[instance] = instance_name
        self.objects[instance_name] = instance
    #    print "Registered instance: ", instance_name, instance
        
    def add(self, instance):
        try:
            self.objects[instance.__class__.__name__].append(instance)
        except KeyError:
            self.objects[instance.__class__.__name__] = [instance]
            
    def __contains__(self, component):
        if (component in self.objects.keys() or
            component in itertools.chain(self.objects.values())):
            return True

    def update(self, environment):
        """ Updates the fields of the environment. This is currently
            unused and may be deprecated. """
        for instruction in environment.Instructions:
            heapq.heappush(self.Instructions, instruction)

        self.objects.update(objects)
        self.parents.update(environment.parents)
        self.references_to.update(environment.references_to)
        self.instance_count.update(environment.instance_count)


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
        heapq.heappush(environment.Instructions,
                      (timer_function() + priority, self, callback))

    def __str__(self):
        return "Instruction({}.{}, {}, {})".format(self.component_name, self.method,
                                                   self.args, self.kwargs)

environment = Environment()
objects = environment.objects

# Things must be done in this order for Alert_Handler to exist inside this file
# and reuse Base machinery, namely for argument parsing. 
import pride.base

import pride.patch
sys = pride.patch.Patched_sys()

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

    def _alert(self, message, level, format_args=tuple()):
        formatted = False
        assert level is not ''
        if level in self._print_level or level is 0:
            formatted = True
            message = message.format(*format_args) if format_args else message
            sys.stdout.write(message + "\n")
        if level in self._log_level or level is 0:
            if not formatted and format_args:
                message = message.format(*format_args)
            severity = self.level_map.get(level, str(level))            
            self.log.seek(0, 1) # windows might complain about files in + mode if this isn't done
            self.log.write(severity + message + "\n")

alert_handler = Alert_Handler()
