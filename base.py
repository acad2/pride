#   mpf.base - root inheritance objects, many framework features are defined here
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

import mmap
import inspect
import sys
import argparse
import traceback
import functools
import heapq
import ast
import types
import importlib
from copy import copy

import mpre
import defaults
import utilities
timer_function = utilities.timer_function

Component_Memory = mpre.Component_Memory
Component_Resolve = mpre.Component_Resolve
Parallel_Instructions = mpre.Parallel_Instructions
Parents = mpre.Parents
References_To = mpre.References_To

from threading import Lock

memlock = Lock()

class Docstring(object):
    
    def __init__(self):
        super(Docstring, self).__init__()

    def __get__(self, instance, _class):
        _object = instance if instance else _class
        return utilities.documentation(_object)
        
        
class Documented(type):
    
    def __new__(cls, name, bases, attributes):
        Documented.make_docstring(attributes)
        return super(Documented, cls).__new__(cls, name, bases, attributes)
        
    @staticmethod
    def make_docstring(attributes):
        attributes["__doc"] = attributes.get("__doc__", "No docstring found")
        attributes["__doc__"] = Docstring()
        
        
class Runtime_Decorator(object):
    """provides the ability to call a function with a decorator specified via
    keyword argument.

    example: my_function(my_argument1, decorator="decoratorlibary.Tracer")"""
    __metaclass__ = Documented
    
    def __init__(self, function):
        self.function = function
        functools.update_wrapper(self, function)
        self.handler_map = {"monkey_patch" : self._handle_monkey_patch,
                            "decorator" : self._handle_decorator,
                            "decorators" : self._handle_decorators}
            
    def __call__(self, *args, **kwargs):
        check_for = kwargs.pop
        modifiers = ("monkey_patch", "decorator", "decorators")
        
        for modifier in modifiers:
            found = check_for(modifier, None)
            if found:
                call = self.handler_map[modifier](found)
                break
        else:
            call = self.function
        return call(*args, **kwargs)  
            
    def _handle_context_manager(self, args, kwargs):
        module_name, context_manager_name = self._resolve_string(kwargs.pop("context_manager"))
        module = self._get_module(module_name)
        context_manager = getattr(module, context_manager_name)
        with context_manager():
            result = self.function(*args, **kwargs)
        return result

    def _handle_monkey_patch(self, patch_info):
        module_name, patch_name = self._resolve_string(patch_info)
        module = self._get_module(module_name)
        monkey_patch = getattr(module, patch_name)
        try:
            result = functools.partial(monkey_patch, self.function.im_self)
        except AttributeError: # function has no attribute im_self (not a method)
            result = monkey_patch
        return result

    def _handle_decorator(self, decorator_type):
        module_name, decorator_name = self._resolve_string(decorator_type)
        decorator = self._get_decorator(decorator_name, module_name)
        return decorator(self.function)

    def _handle_decorators(self, decorator_names):
        decorators = []
        for item in decorator_names:
            module_name, decorator_name = self._resolve_string(item)
            decorator = self._get_decorator(decorator_name, module_name)
            decorators.append(decorator)

        wrapped_function = self.function
        for item in reversed(decorators):
            wrapped_function = item(wrapped_function)
        return wrapped_function

    def _resolve_string(self, string):
        try: # attempt to split the string into a module and attribute
            module_name, decorator_name = string.split(".")
        except ValueError: # there was no ".", it's just a single attribute
            module_name = "__main__"
            decorator_name = string
        finally:
            return module_name, decorator_name

    def _get_module(self, module_name):
        try: # attempt to load the module if it exists already
            module = sys.modules[module_name]
        except KeyError: # import it if it doesn't
            module = __import__(module_name)
        finally:
            return module

    def _get_decorator(self, decorator_name, module_name):
        module = self._get_module(module_name)
        return getattr(module, decorator_name)


class Parser(object):
    sys_argv_backup = copy(sys.argv)
    __metaclass__ = Documented
    
    def __init__(self, parser, modifiers, exit_on_help, name):
        super(Parser, self).__init__()
        self.parser = parser
        self.modifiers = modifiers
        self.exit_on_help = exit_on_help
        self.name = name

    def get_arguments(self, argument_info):
        arguments = {}
        argument_names = argument_info.keys()
        switch = {"short" : "-",
                  "long" : "--",
                  "positional" : ""}

        default_modifiers = {"types" : ("long", )}
        self_modifiers = self.modifiers
        for name in argument_names:
            modifiers = self_modifiers.get(name, default_modifiers)
            if modifiers == "ignore":
                continue
            info = {}
            for keyword_argument, value in modifiers.items():
                info[keyword_argument] = value

            temporary = {}
            for arg_type in info.pop("types"):
                if arg_type != "positional":
                    temporary["dest"] = name

                default_value = argument_info[name]
                temporary["default"] = default_value
                value_type = type(default_value)
                if value_type == bool:
                    value_type = ast.literal_eval
                temporary["type"] = value_type

                for key, value in temporary.items():
                    info.setdefault(key, value)

                arg_name = switch[arg_type] + name
                arguments[arg_name] = info

        parser = self.parser
        exit_on_help = self.exit_on_help

        for argument_name, options in arguments.items():
            parser.add_argument(argument_name, **options)

        new_argv = copy(Parser.sys_argv_backup)
        sys.argv = new_argv

        try:
            arguments, unused = parser.parse_known_args()
        except SystemExit:
            if exit_on_help:
                raise
            try:
                new_argv.pop(new_argv.index("-h"))
            except ValueError:
                new_argv.pop(new_argv.index("--help"))
            arguments, unused = parser.parse_known_args()

        if unused:
          #  new_argv = copy(Parser.sys_argv_backup)
            for unused_name in unused:
                index = new_argv.index(unused_name)
                new_argv.pop(index)

                if "-" in unused_name: # pop whatever the value for the positional arg was too
                    try:
                        word = new_argv.pop(index)
                    except IndexError: # no argument supplied to positional arg
                        pass
                    else:
                        try:
                            unused.remove(word)
                        except ValueError:
                            pass

            arguments, unused = parser.parse_known_args()
            sys.argv = copy(Parser.sys_argv_backup)
        return arguments

    def get_options(self, argument_info):
        namespace = self.get_arguments(argument_info)
        options = dict((key, getattr(namespace, key)) for key in namespace.__dict__.keys())
        return options

        
class Metaclass(Documented):
    """Includes class.defaults attribute/values in docstrings.\nApplies the Runtime_Decorator to class methods.\nAdds instance trackers to classes."""
    
    #__metaclass__ = Documented # this actually works
    parser = argparse.ArgumentParser()
    command_parser = parser.add_subparsers(help="filename")
    run_parser = command_parser.add_parser("run", help="execute the specified script")
    profile_parser = command_parser.add_parser("profile", help="profile the specified script")

    enable_runtime_decoration = True

    def __new__(cls, name, bases, attributes):
        new_class = super(Metaclass, cls).__new__(cls, name, bases, attributes)
        new_class.instance_tracker = {}
        new_class.instance_count = 0
        # parser
        exit_on_help = attributes.get("exit_on_help", True)

        base_class = bases[0]
        modifiers = getattr(base_class, "parser_modifiers", {}).copy()

        parser_ignore = set()
        new_parser_ignore = attributes.get("parser_ignore", tuple())
        old_parser_ignore = getattr(base_class, "parser_ignore", tuple())
        for ignore in new_parser_ignore + old_parser_ignore:
            parser_ignore.add(ignore)
        new_class.parser_ignore = tuple(parser_ignore)
        for attribute in parser_ignore:
            modifiers[attribute] = "ignore"

        new_modifiers = attributes.get("parser_modifiers", {})
        modifiers.update(new_modifiers)
        Metaclass.make_parser(new_class, name, modifiers, exit_on_help)

        if Metaclass.enable_runtime_decoration:
            Metaclass.decorate(cls, new_class, attributes)
        return new_class

    @staticmethod
    def make_parser(new_class, name, modifiers, exit_on_help):
        parser = Metaclass.command_parser.add_parser(name)
        new_class.parser = Parser(parser, modifiers, exit_on_help, name)

    @staticmethod
    def decorate(cls, new_class, attributes):
        for key, value in new_class.__dict__.items():
            if key[0] != "_" and callable(value):
                bound_method = types.MethodType(Runtime_Decorator(value), 
                                                None, 
                                                new_class)
                setattr(new_class, key, bound_method)
        return new_class


class Instruction(object):
    
    def _get_execute_at(self):
        return self.created_at + self.priority
    execute_at = property(_get_execute_at)
    log_processor_time = False

    def _get_call(self):
        return self.method, self.args, self.kwargs
    call = property(_get_call)
    
    def __init__(self, component_name, method, *args, **kwargs):
        super(Instruction, self).__init__()
        self.component_name = component_name
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.priority = 0.0

    def execute(self):
        self.created_at = timer_function()
        heapq.heappush(mpre.Instructions, (self.execute_at, self))
            
    def __str__(self):
        args = self.args
        kwargs = self.kwargs
        number_of_formats = len(args)
        arg_string = ", ".join("{0}".format(args[index]) for index in xrange(number_of_formats))
        kwarg_string = ", ".join("{0}={1}".format(attr, value) for attr, value in kwargs.items())
        format_arguments = (self.component_name, self.method)#, arg_string, kwarg_string)
        return "Instruction {0}.{1}".format(*format_arguments)


class Alert(object):

    log_level = 0
    print_level = 0
    log = open("Alerts.log", "a")
    level_map = {0 : "Error ",
                'v' : "notification ",
                'vv' : "verbose notification ",
                'vvv' : "very verbose notification ",
                'vvvv' : "extremely verbose notification "}

                
class Base(object):
    """A base object to inherit from. An object that inherits from base
    can have arbitrary attributes set upon object instantiation by specifying
    them as keyword arguments. An object that inherits from base will also
    be able to create/hold arbitrary python objects by specifying them as
    arguments to create. Classes that inherit from base should specify a class.defaults 
    dictionary that will automatically include the specified (attribute, value) pairs on 
    all new instances."""
    __metaclass__ = Metaclass
    
    # A command line argument parser is generated automatically for
    # every Base class based upon the attributes contained in the
    # class defaults dictionary. Specific attributes can be modified
    # or ignored by specifying them here.
    parser_modifiers = {}
    parser_ignore = ("network_packet_size", "memory_size")
    
    # public methods are methods that are available for direct use
    # by external objects without requiring use of Instructions or
    # message sending. Public methods are typically short and vital
    # to the operation of the class that offers them 
    # i.e. Asynchronous_Network.buffer_data and add are public methods
    public_methods = tuple()
    
    # the default attributes an instance will initialize with.
    # storing them here and using the attribute_setter method
    # makes them modifiable at runtime and eliminates the need
    # to type out the usual self.attribute = value statements
    defaults = defaults.Base
    
    def _get_parent(self):
        return Parents[self]
    parent = property(_get_parent)
    
    def __init__(self, **kwargs):
        super(Base, self).__init__()
        self._return_to = {}
        
        # register name + number
        cls = type(self)
        
        instance_number = self.instance_number = cls.instance_count
        cls.instance_tracker[instance_number] = self
        cls.instance_count += 1
        
        ending = str(instance_number) if instance_number else ''
        name = self.instance_name = cls.__name__ + ending
        Component_Resolve[name] = self
        
        # mutable datatypes (i.e. containers) should not be used inside the
        # defaults dictionary and should be set in the call to __init__
        self.objects = {}

        # instance attributes are assigned via kwargs
        attributes = self.defaults.copy()
        attributes.update(kwargs)
        if kwargs.get("parse_args"):
            attributes.update(self.parser.get_options(attributes))
                
        self.attribute_setter(**attributes)
               
        if self.memory_size:
            memory = mmap.mmap(-1, self.memory_size)
            Component_Memory[name] = memory, []

    def attribute_setter(self, **kwargs):
        """usage: object.attribute_setter(attr1=value1, attr2=value2).
        called implicitly in __init__ for any object that inherits from Base."""
        [setattr(self, attr, val) for attr, val in kwargs.items()]

    def create(self, instance_type, *args, **kwargs):
        """usage: object.create("module_name.object_name", args, kwargs)

        The specified python object will be instantiated with the given arguments
        and placed inside object.objects under the created objects class name via
        the add method"""
        if not isinstance(instance_type, type):
            instance_type = self._resolve_string(instance_type)
                    
        # instantiate the new object from a class object
        instance = instance_type(*args, **kwargs)

        self.add(instance)
        Parents[instance] = self.instance_name
        return instance

    def delete(self):
        """usage: object.delete() or object.delete(child). thoroughly untested."""
        assert not self.deleted
        self.deleted = True
        
        name = self.instance_name
                
        del self.instance_tracker[self.instance_number]
       
        # changing a list while iterating through it produces non intuitive results
        # copies have to be made
        for child_type, children in self.objects.items():
            children_names = [child.instance_name for child in children]
            for _name in children_names:
                Component_Resolve[_name].delete()
                
        print "deleting references to", self
        names = [instance_name for instance_name in References_To[self]]
        for instance_name in names:
            instance = Component_Resolve[instance_name]
            instance.remove(self)

        del Component_Resolve[name]
        if self.memory_size:
            del Component_Memory[name]      
       # print "\nFinished deleting {}".format(self.instance_name)

    def remove(self, instance):
        """Usage: object.remove(instance)
        
        Removes an instance from self.objects"""
        self.objects[instance.__class__.__name__].remove(instance)
        References_To[instance].remove(self.instance_name)
                
    def add(self, instance):
        """usage: object.add(instance)

        adds an instance to the instances' class name entry in parent.objects.
        """        
        references = References_To.get(instance, set())
        
        objects = self.objects
        instance_class = instance.__class__.__name__
        siblings = objects.get(instance_class, [])  
                        
        if instance not in siblings:
            siblings.append(instance)
            objects[instance_class] = siblings
            references.add(self.instance_name)
            References_To[instance] = references            
                
    def alert(self, message="Unspecified alert message",
                    format_args=tuple(),
                    level=0,
                    callback=None, callback_instruction=None):
        """usage: base.alert(message, format_args, level, callback, callback_instruction)

        Create an alert. Depending on the level given, the alert may be printed
        for immediate attention and/or logged quietly for later viewing.

        -message is a string that will be logged and/or displayed
        -format_args are any string formatting args for message.format()
        -level is a small integer indicating the severity of the alert.
        -callback is an optional tuple of (function, args, kwargs) to be called when
        the alert is triggered
        -callback_instruction is an optional Instruction to be posted when the alert is triggered.

        alert severity is relative to the Alert.log_level and Alert.print_level;
        a lower number indicates a less verbose notification, while 0 indicates
        an error or exception and will never be suppressed."""

        if self.verbosity >= level:
            message = self.instance_name + ": " + message.format(*format_args)
            if not Alert.print_level or level <= Alert.print_level:
                sys.stdout.write(message + "\n")
            if level <= Alert.log_level:
                severity = Alert.level_map.get(level, str(level))
                Alert.log.write(severity + message + "\n")
            if callback_instruction:
                callback_instruction.execute()
            if callback:
                function, args, kwargs = callback
                return function(*args, **kwargs)
                        
    def public_method(self, component_name, method_name, *args, **kwargs):
        """usage: base.public_method(component_name, method_name, *args, **kwargs) =>
                  component.method(*args, **kwargs)
                  
           Used to call the method of an external object directly without using 
           instructions or message sending/reading. Public methods are designated in
           the public_methods field of a class object. Attempting to call a
           public_method on an object that does not specify the method as public
           will result in a ValueError. This call is not scheduled by the processor
           and happens immediately. The return value from the external method is 
           returned by this call."""
        component = Component_Resolve[component_name]
        if method_name in component.public_methods:
            return getattr(component, method_name)(*args, **kwargs)
        else:
            raise ValueError
    
    def rpc(self, component_name, message,
            _response_to="None"):
        """Usage: component.send(component_name, message)
        
        Writes the supplied message to the memory owned by component_name.
        Internally, an index to the end of the message is stored for later retrieval.
        
            - component_name is a base_object.instance_name
            - message can be bytes or a string"""
        #if memlock.locked():
        #    print "concurrency error !"
       #     raise SystemExit
      #  memlock.acquire()
        memory, pointers = Component_Memory[component_name]
        Parallel_Instructions.append(component_name)
        
        reaction = ''
        if message[:6] == "return":
            flag, reaction, message = message.split(" ", 2)
            
        id, packet = self._make_packet(_response_to, message)
        if reaction:
            self._return_to[id] = reaction
        
        memory.write(packet)
        pointers.append((self.instance_name, memory.tell()))
       # memlock.release()
        
    def read_messages(self):
        """Usage: component.read_messages => [message1, message2, ...]
        
        Returns a list of messages. The list contains all messages sent via
        the rpc method since the last call to read_messages. Messages in the list
        are of the bytes/string type"""

        name = self.instance_name
        memory, pointers = Component_Memory[name]
        
        messages = []
        if pointers:
            old_pointer = 0
            for sender, pointer in pointers:
                messages.append((sender, memory[old_pointer:pointer]))
                old_pointer = pointer
            memory.seek(0)
            Component_Memory[name] = memory, []
        
        return messages

    def _make_packet(self, response_to, data):
        message = response_to + " " + data
        id = str(hash(message))
        return id, id + " " + message
        
    def react(self):        
        for sender, packet in self.read_messages():
    #        print "Received packet: ", packet
            id, response_to, data = packet.split(" ", 2)            
            
            if response_to in self._return_to:
                command = self._return_to[response_to]
                old_command, value = data.split(" ", 1)
            else:
                command, value = data.split(" ", 1)
                                       
            self.alert("handling response {} {}",
                       [command, value[:32]],
                       level='vv')
    #        print "reaction: ", self.instance_name, command, value
            response = getattr(self, command)(sender, value)
            
            if response:                                
                self.alert("Sending response: {} in response to {}",
                           [response, id],
                           level='vvv')
                self.rpc(sender, response, id)
            
    def _resolve_string(self, string):
        """Given a string of ...x.y.z, import ...x.y and return an instance of z"""
        module_name = string.split(".")   
        class_name = module_name.pop(-1)
        module_name = '.'.join(module_name)
        if not module_name:
            module_name = "__main__"
            
        _from = sys.modules[module_name] if module_name in sys.modules\
                else importlib.import_module(module_name)

        return getattr(_from, class_name)
        
            
class Wrapper(Base):
    """a class that will act as the object it wraps and as an
       Rpc_Enabled Base object simultaneously."""

    def __init__(self, **kwargs):
        """attributes = {"wrapped_object" : wrapped_object, "objects" : {}, "added_to" : set()}
        if kwargs:
            attributes.update(kwargs)
        super(Wrapper, self).attribute_setter(**attributes)"""
        wraps = super(Wrapper, self).__getattribute__("wraps")
        try:
            wrapped_object = kwargs.pop("wrapped_object")
        except KeyError:
            pass
        else:
            wraps(wrapped_object)
        super(Wrapper, self).__init__(**kwargs)

    def wraps(self, obj, set_defaults=False):
        set_attr = super(Wrapper, self).__setattr__
        if set_defaults:
            for attribute, value in self.defaults.items():
                set_attr(attribute, value)
        set_attr("wrapped_object", obj)

    def __getattribute__(self, attribute):
        try:
            wrapped_object = super(Wrapper, self).__getattribute__("wrapped_object")
            value = super(type(wrapped_object), wrapped_object).__getattribute__(attribute)
        except AttributeError:
            value = super(Wrapper, self).__getattribute__(attribute)
        return value

    def __setattr__(self, attribute, value):
        try:
            wrapped_object = self.wrapped_object
            super(type(wrapped_object), wrapped_object).__setattr__(attribute, value)
        except AttributeError:
            super(Wrapper, self).__setattr__(attribute, value)      