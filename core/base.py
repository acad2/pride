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
import pickle
import inspect
import time
import sys
import argparse
import traceback
import functools
import heapq
import ast
from copy import copy
from types import MethodType
from weakref import proxy, ref

import defaults
import utilities

Component_Memory = {} 
Component_Resolve = {}

class Event(object):
    
    events = []
            
    def __init__(self, component_name, method, *args, **kwargs):
        super(Event, self).__init__()
        self.component_name = component_name
        self.method = method # any method can be supplied
        self.args = args # any arguments can be supplied
        self.kwargs = kwargs # any keyword arguments can be supplied
        priority = kwargs.setdefault("priority", .04)
        
        try: # supplying the component foregoes the need for a lookup
            self.component = kwargs.pop("component")
        except KeyError:
            self.component = None
            
        if method != "create":
            del kwargs["priority"]
        self.execute_at = priority + utilities.timer_function()
        
    def post(self):
        heapq.heappush(Event.events, (self.execute_at, self))
        
    def __str__(self):
        args = self.args
        kwargs = self.kwargs
        number_of_formats = len(args)
        arg_string = ", ".join("{0}".format(args[index]) for index in xrange(number_of_formats))
        kwarg_string = ", ".join("{0}={1}".format(attr, value) for attr, value in kwargs.items())
        format_arguments = (self.component_name, self.method, arg_string, kwarg_string)
        return "Event {0}.{1}({2}, {3})".format(*format_arguments)
        
    def execute_code(self):    
        call = getattr(self.component, self.method)
        try:
            result = call(*self.args, **self.kwargs)   
        except BaseException as result:
            result.traceback = traceback.format_exc()
            raise result
        return result
        
        
class Runtime_Decorator(object):
    """provides the ability to call a function with a decorator specified via
    keyword argument.
    
    example: my_function(my_argument1, decorator="decoratorlibary.Tracer")"""
    
    def __init__(self, function):
        self.function = function        
    
    def __call__(self, *args, **kwargs):
        #print self.function, args, kwargs
        
        if kwargs.has_key("context_manager"):
            module_name, context_manager_name = self._resolve_string(kwargs.pop("context_manager"))
            module = self._get_module(module_name)
            context_manager = getattr(module, context_manager_name)
            with context_manager():
                result = self.function(*args, **kwargs)
                
        elif kwargs.has_key("monkey_patch"):
            module_name, patch_name = self._resolve_string(kwargs.pop("monkey_patch"))
            module = self._get_module(module_name)
            monkey_patch = getattr(module, patch_name)
            result = monkey_patch(self.function.im_self, *args, **kwargs)
            
        elif kwargs.has_key('decorator'):
            decorator_type = kwargs.pop("decorator")            
            module_name, decorator_name = self._resolve_string(decorator_type)
            decorator = self._get_decorator(decorator_name, module_name)
            wrapped_function = decorator(self.function)
            result = wrapped_function(*args, **kwargs)

        elif kwargs.has_key('decorators'):
            decorators = []
            decorator_names = kwargs.pop("decorators")
            for item in decorator_names:
                module_name, decorator_name = self._resolve_string(item)
                decorator = self._get_decorator(decorator_name, module_name)
                decorators.append(decorator)

            wrapped_function = self.function
            for item in reversed(decorators):
                wrapped_function = item(wrapped_function)            
            result = wrapped_function(*args, **kwargs)
        
        else:
            result = self.function(*args, **kwargs)
        return result
        
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
        try: # attempt to procure the decorator class
            decorator_wrap = getattr(module, decorator_name)
        except AttributeError: # decorator not found in module
            print("failed to locate decorators %s for function %s." %\
            (decorator_name, self.function))
        else:
            return decorator_wrap # instantiate the class with self.function

            
class Docstring(object):
    
    def __init__(self):
        super(Docstring, self).__init__()
        
    def __get__(self, instance, _class):
        if instance:
            _object = instance
        else:
            _object = _class
        return utilities.documentation(_object)
                

class Parser(object):
    sys_argv_backup = copy(sys.argv)
    
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

        
class Metaclass(type):
    """Includes class.defaults attribute/values in docstrings. Applies the
    Runtime_Decorator to class methods. Adds instance trackers to classes."""
    
    parser = argparse.ArgumentParser()  
    command_parser = parser.add_subparsers(help="filename")
    run_parser = command_parser.add_parser("run", help="execute the specified script")
    profile_parser = command_parser.add_parser("profile", help="profile the specified script")  
    
    enable_runtime_decoration = True
    
    def __new__(cls, name, bases, attributes):
        Metaclass.make_docstring(attributes)
                
        attributes["instance_tracker"] = {}
        attributes["instance_count"] = 0
        new_class = type.__new__(cls, name, bases, attributes)
        
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
    def make_docstring(attributes):
        try:
            docstring = attributes["__doc__"]
        except KeyError:
            docstring = "No docstring found. Only introspected information available\n"
        attributes["__doc"] = docstring
        attributes["__doc__"] = Docstring()
    
    @staticmethod    
    def make_parser(new_class, name, modifiers, exit_on_help):
        parser = Metaclass.command_parser.add_parser(name)
        new_class.parser = Parser(parser, modifiers, exit_on_help, name)
                
    @staticmethod
    def decorate(cls, new_class, attributes):
        for key, value in new_class.__dict__.items():
            if key[0] != "_" and callable(value):
                wrapped = Runtime_Decorator(value)
                functools.update_wrapper(wrapped, value)
                bound_method = MethodType(wrapped, None, new_class)
                setattr(new_class, key, bound_method)                
        return new_class
            

class Alert(object):
    
    log_level = 4
    print_level = 3
    log = open("Alerts.log", "w+")
    level_map = {0 : "very very verbose notification ",
                 1 : "very verbose notification ",
                 2 : "verbose notification ",
                 3 : "notification ",
                 4 : "warning ",
                 5 : "error "}
            
        
class Base(object):
    """A base object to inherit from. an object that inherits from base 
    can have arbitrary attributes set upon object instantiation by specifying 
    them as keyword arguments. An object that inherits from base will also 
    be able to create/hold arbitrary python objects by specifying them as 
    arguments to create.
    
    classes that inherit from base should specify a class.defaults dictionary that will automatically
    include the specified (attribute, value) pairs on all new instances"""
    __metaclass__ = Metaclass
    parser_modifiers = {}
    parser_ignore = ("network_packet_size", "memory_size")
    # the default attributes an instance will initialize with.
    # storing them here and using the attribute_setter method
    # makes them modifiable at runtime and eliminates the need
    # to type out the usual self.attribute = value statements
    defaults = defaults.Base
     
    def _get_name(self):
        name = type(self).__name__
        instance_number = self.instance_number
        if instance_number:
            name += str(instance_number)
        return name
    instance_name = property(_get_name)
    
    def __new__(cls, *args, **kwargs):               
        instance = super(Base, cls).__new__(cls, *args, **kwargs)
        instance_number = instance.instance_number = cls.instance_count
        cls.instance_tracker[instance_number] = instance
        cls.instance_count += 1
        return instance
        
    def __init__(self, **kwargs):
        super(Base, self).__init__()
        
        # mutable datatypes (i.e. containers) should not be used inside the
        # defaults dictionary and should be set in the call to __init__
        self.objects = {}
        
        # instance attributes are assigned via kwargs
        attributes = self.defaults.copy()        
        if "parse_args" in kwargs and kwargs["parse_args"]:
            attributes.update(self.parser.get_options(attributes))
        attributes.update(kwargs)
        self.attribute_setter(**attributes)     
        
        name = self.instance_name
        Component_Resolve[name] = self        
        if self.memory_size:
            memory = mmap.mmap(-1, self.memory_size)             
            Component_Memory[name] = memory 
            
    def attribute_setter(self, **kwargs):
        """usage: object.attribute_setter(attr1=value1, attr2=value2).
        called implicitly in __init__ for any object that inherits from Base."""   
        [setattr(self, attr, val) for attr, val in kwargs.items()]
                     
    def create(self, instance_type, *args, **kwargs): 
        """usage: object.create("module_name.object_name", args, kwargs)
        
        The specified python object will be instantiated with the given arguments
        and placed inside object.objects under the created objects class name via 
        the add method"""
        kwargs.setdefault("parent", self)
                        
        # resolve string to actual class
        try:
            names = instance_type.split(".")
        except AttributeError:
            pass
        else:
            module_name = names.pop(0)
            module_name = module_name.replace("metapython", "__main__")
            if module_name in sys.modules:
                _from = sys.modules[module_name]
            else:
                _from = __import__(module_name)
                
            for name in names:                
                _from = getattr(_from, name)
            instance_type = _from
        
        # instantiate the new object from a class object
        # if the object does not accept the attempted supplied kwargs (such as
        # the above-set parent attribute), then it is wrapped so it can
        try:
    #        print "attempting to instantiate", instance_type, args, kwargs, "\n"
            instance = instance_type(*args, **kwargs)
        except BaseException as error:
            raise
            if error in (SystemExit, KeyboardInterrupt):
                raise
            trace = traceback.format_exc() + "\n"            
            try:
                instance = instance_type(*args)
            except:
                print "real exception encountered when creating {0}".format(instance_type)
                print trace
                raise error            
            kwargs["wrapped_object"] = instance
            instance = Wrapper(**kwargs)
        
        instance.added_to = set()
        self.add(instance)       
        return instance
 
    def delete(self):
        """usage: object.delete() or object.delete(child). thoroughly untested."""
        #print "deleting {0} from".format(self.instance_name), Component_Resolve.keys()
        del Component_Resolve[self.instance_name]
        if self.memory_size:
            del Component_Memory[self.instance_name]
        del type(self).instance_tracker[self.instance_number]
        
        class_name = type(self).__name__
        for instance_name in self.added_to:
            instance = Component_Resolve[instance_name]
         #   print "removing %s from %s" % (self.instance_name, instance_name)
            instance.remove(self)             
        
        for child in self.get_children():
            child.delete()   
            
    def remove(self, *args):
        for arg in args:
            self.objects[arg.__class__.__name__].remove(arg)
            
    def add(self, instance):
        """usage: object.add(other_object)

        adds an already existing object to the instances' class name entry in parent.objects.
        """        
        if not hasattr(instance, "parent"):
            instance.parent = self # is a reference problem without reference tracking in place
        instance.added_to.add(self.instance_name)        
        try:
            self.objects[instance.__class__.__name__].append(instance)
        except KeyError:
            self.objects[instance.__class__.__name__] = [instance]
        
    def send_to(self, component_name, message):
        Component_Memory[component_name].write(message+"delimiter")
        
    def read_messages(self):
        memory = Component_Memory[self.instance_name]
        memory.seek(0)
        data = memory.read(self.memory_size)
        memory.seek(0)
        if data.count("delimiter"):
            size = len(data) 
            messages = data.split("delimiter")[:-1]
            memory.write("\x00"*size)
            memory.seek(0)
        else:
            messages = []        
        return messages

    def alert(self, message="Unspecified message", level=0, callback=None, callback_event=None):
        """usage: base.alert(message, level, callback, callback_event)
        
        Create an alert. Depending on the level given, the alert may be printed
        for immediate attention and/or logged quietly for later viewing. 
        
        -message is a string that will be logged and/or displayed
        -level is a small integer indicating the severity of the alert. 
        -callback is an optional tuple of (function, args, kwargs) to be called when
        the alert is triggered
        -callback_event is an optional Event to be posted when the alert is triggered.
        
        alert severity is relative to the Alert.log_level and Alert.print_level;
        a lower number indicates a less verbose notification, while 0 indicates
        an error or exception and will never be suppressed"""  
        if level <= self.verbosity:
            if (level >= Alert.print_level):
                sys.stdout.write(message + "\n>>> ")                
            if level >= Alert.log_level:
                severity = Alert.level_map.get(level, str(level))
                Alert.log.write(severity + message + "\n")        
            if callback_event:
                callback_event.post()
            if callback:
                function, args, kwargs = callback
                return function(*args, **kwargs)
            
    def get_children(self):
        """usage: for child in object.get_children...
        
        Creates a generator that yields the immediate children of the object."""
        for _list in self.objects.values():
            for child in _list:
                yield child
                
    def get_family_tree(self):
        """usage: all_objects = object.get_family_tree()
        
        returns a dictionary containing all the children/descendants of object"""
        tree = {self : []}
        for instance in self.get_children():
            tree[self].append(proxy(instance))
            tree.update(instance.get_family_tree())
        return tree    
        
    def _get_source(self):
        return inspect.getsource(self.__class__)
    source = property(_get_source)
    
    
class Wrapper(Base):
    """a class that will act as the object it wraps and as a base
    object simultaneously."""
        
    def __init__(self, **kwargs):
        """attributes = {"wrapped_object" : wrapped_object, "objects" : {}, "added_to" : set()}
        if kwargs:
            attributes.update(kwargs)
        super(Wrapper, self).attribute_setter(**attributes)"""
        wraps_method = super(Wrapper, self).__getattribute__("wraps")
        wraps_method(kwargs.pop("wrapped_object"))
        super(Wrapper, self).__init__(**kwargs)
                
    def wraps(self, obj):
        super(Wrapper, self).__setattr__("wrapped_object", obj)
        
    def __getattribute__(self, attribute): 
        wrapped_object = super(Wrapper, self).__getattribute__("wrapped_object")
        try:
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
        
    def __dir__(self):
        return dir(super(Wrapper, self).__getattribute__("wrapped_object"))

    def __str__(self):
        try:
            name = str(super(Wrapper, self).__getattribute__("wrapped_object"))
        except AttributeError:
            name = ""
        return "Wrapped(%s)" % name

    def __repr__(self):
        return super(Wrapper, self).__repr__()

                                
class Process(Base):
    """a base process for processes to subclass from. Processes are managed
    by the system. The start method begins a process while the run method contains
    the actual code to be executed every frame."""
    
    defaults = defaults.Process
    parser_ignore = ("auto_start", "network_buffer", "keyboard_input", "stdin_buffer_size")

    def __init__(self, **kwargs):
        self.args = tuple()
        self.kwargs = dict()
        super(Process, self).__init__(**kwargs)
        if self.stdin_buffer_size:
            self.stdin_buffer = mmap.mmap(-1, self.stdin_buffer_size)
            Event("User_Input0", "add_buffer", self.stdin_buffer).post()
            
        if self.auto_start:
            args = (self.instance_name, "start")
            options = {"component" : self,
                       "priority" : 0.0}
            Event(*args, **options).post()
    
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
        self.alert("set {0} priority to {1}".format(self, self.priority), 0)
        Event(*args, **options).post()
        
    def propagate(self):
        if self in self.parent.objects[self.__class__.__name__]:
            options = {"component" : self,
                       "priority" : self.priority}
            Event(self.instance_name, "run", **options).post()
        
        
class Thread(Base):
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

    
# for vmlibrary.Machines
class Hardware_Device(Base):
    
    defaults = defaults.Hardware_Device
    
    def __init__(self, **kwargs):
        super(Hardware_Device, self).__init__(**kwargs)
        