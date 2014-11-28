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
from types import MethodType
from weakref import proxy, ref

import defaults
import utilities

Component_Memory = {} 
Component_Resolve = {}

if "win" in sys.platform:
    timer_function = time.clock
else:
    timer_function = time.time  


class Event(object):
    
    events = []
            
    def __init__(self, component_name, method, *args, **kwargs):
        super(Event, self).__init__()
        self.component_name = component_name
        self.method = method # any method can be supplied
        self.args = args # any arguments can be supplied
        self.kwargs = kwargs # any keyword arguments can be supplied
            
        try: # supplying the component foregoes the need for a lookup
            self.component = kwargs.pop("component")
        except KeyError:
            self.component = None
        try: # for process scheduler, priority is in seconds
            priority = self.priority = kwargs.pop("priority")
        except KeyError:
            priority = self.priority = .04 # 25 fps
        self.execute_at = priority + timer_function()
        
    def post(self):
        heapq.heappush(Event.events, (self.execute_at, self))
        
    def __str__(self):
        number_of_formats = len(self.args)
        arg_string = "%s " * number_of_formats
        return "%s_Event: %s " % (self.component_name, self.method) + arg_string % self.args
        
    def execute_code(self):    
        call = getattr(self.component, self.method)
        call(*self.args, **self.kwargs)   
         
        
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
                

class Metaclass(type):
    """Includes class.defaults attribute/values in docstrings. Applies the
    Runtime_Decorator to class methods. Adds instance trackers to classes."""
    
    parser = argparse.ArgumentParser(description="Base parser", add_help=False)
    subparsers = parser.add_subparsers(help='')
    
    enable_runtime_decoration = True
    
    def __new__(cls, name, bases, attributes):
        Metaclass.make_docstring(attributes)
        #Metaclass.make_parser(cls, attributes) # not implemented
        attributes["instance_tracker"] = {}
        attributes["instance_count"] = 0
        new_class = type.__new__(cls, name, bases, attributes)
        if Metaclass.enable_runtime_decoration:
            Metaclass.decorate(cls, new_class, attributes)
        
        #self.create_parser = self.subparsers.add_parser("create", help="Create objects")
        #self.create_parser.add_argument("create", help="Create a new machine or process")
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
    def make_parser(cls, attributes):
        parser_parents = []
        for parent_class in cls.__mro__:
            parser = getattr(parent_class, "_parser__parser", None)
            if parser:
                parser_parents.append(parent_class._parser__parser)
        cls_parser = argparse.ArgumentParser(parents=parser_parents)
        defaults = attributes.get("defaults", None)
        if defaults:
            for key, value in defaults.items():
                cls_parser.add_argument("--%s" % key, type=type(value), default=value)
        attributes["__parser"] = cls_parser
        
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
    
    # the default attributes an instance will initialize with.
    # storing them here and using the attribute_setter method
    # makes them modifiable at runtime and eliminates the need
    # to type out the usual self.attribute = value statements
    defaults = defaults.Base
     
    def _get_name(self):
        return type(self).__name__ + str(self.instance_number)
    instance_name = property(_get_name)
    
    def __new__(cls, *args, **kwargs):
        instance = super(Base, cls).__new__(cls, *args, **kwargs)
        instance_number = instance.instance_number = cls.instance_count
        cls.instance_tracker[instance_number] = instance
        cls.instance_count += 1
        return instance
        
    def __init__(self, **kwargs):
        # mutable datatypes (i.e. containers) should not be used inside the
        # defaults dictionary and should be set in the __init__, like so
        self.objects = {}
        super(Base, self).__init__()
        attributes = self.defaults.copy()
        if kwargs:
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
        if not kwargs.has_key("parent"):
            kwargs["parent"] = self
            #kwargs["parent_weakref"] = ref(self)
            
        # resolve string to actual class
        if type(instance_type) == str:
            try:
                module, _class = instance_type.split(".")
            except ValueError:
                module, _class = __name__, instance_type
            finally:
                try:
                    module = sys.modules[module]
                except KeyError:
                    module = __import__(module)
                instance_type = getattr(module, _class)
        
        # instantiate the new object from a class object
        # if the object does not accept the attempted supplied kwargs (such as
        # the above-set parent attribute), then it is wrapped so it can
        try:
            #print "attempting to instantiate", instance_type, args, kwargs, "\n"
            instance = instance_type(*args, **kwargs)
        except BaseException as error:
            if error in (SystemExit, KeyboardInterrupt):
                raise
            raise
            self.alert("Exception instantiating {0}, attemping to apply Wrapper...\n{1}".format(\
            instance_type, traceback.format_exc()), 4)
            instance = instance_type(*args)
            instance = Wrapper(instance, **kwargs)
        instance.added_to = set()
        self.add(instance)       
        return instance
 
    def delete(self):
        """usage: object.delete() or object.delete(child). thoroughly untested."""
        del Component_Resolve[self.instance_name]
        del Component_Memory[self.instance_name]
        del type(self).instance_tracker[self.instance_number]
        for child in self.get_children():
            child.delete()
        class_name = type(self).__name__
        for instance_name in self.added_to:
            instance = Component_Resolve[instance_name]
         #   print "removing %s from %s" % (self.instance_name, instance_name)
            instance.remove(self)             
            
    def remove(self, *args):
        for arg in args:
            self.objects[arg.__class__.__name__].remove(arg)
            
    def add(self, instance):
        """usage: object.add(other_object)

        adds an already existing object to the instances' class name entry in parent.objects.
        """        
        if not hasattr(instance, "parent"):
            instance.parent = self # is a reference problem without stm in place
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

    def alert(self, message="Unspecified message", level=4, callback=None, callback_event=None):
        """usage: base.alert(message, level, callback, callback_event)
        
        Create an alert. Depending on the level given, the alert may be printed
        for immediate attention and/or logged quietly for later viewing. 
        
        -message is a string that will be logged and/or displayed
        -level is a small integer indicating the severity of the alert. 
        -callback is an optional tuple of (function, args, kwargs) to be called when
        the alert is triggered
        -callback_event is an optional Event to be posted when the alert is triggered.
        
        alert severity is relative to the Alert.log_level and Alert.print_level;
        a lower number indicates a less verbose/severe notification."""
        if not self.ignore_alerts:
            if (level >= Alert.print_level):
                print message
            if level >= Alert.log_level:
                severity = Alert.level_map[level]
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
    

class Wrapper(Base):
    """a class that will act as the object it wraps and as a base
    object simultaneously."""
       
    def __init__(self, wrapped_object=None, **kwargs):
        """attributes = {"wrapped_object" : wrapped_object, "objects" : {}, "added_to" : set()}
        default_kwargs = super(Wrapper, self).__getattribute__("defaults")
        if default_kwargs:
            attributes.update(default_kwargs)
        if kwargs:
            attributes.update(kwargs)
        super(Wrapper, self).attribute_setter(**attributes)"""
        kwargs["wrapped_object"] = wrapped_object
        super(Wrapper, self).__init__(**kwargs)
                       
    def _get_wrapper_attribute(self, attribute):
        return super(Wrapper, self).__getattribute__(attribute)

    def __getattribute__(self, attribute): 
        try:
            wrapped_object = super(Wrapper, self).__getattribute__("wrapped_object")
        except AttributeError:
            return super(Wrapper, self).__getattribute__(attribute)            
        try:
            attr = getattr(wrapped_object, attribute)
        except AttributeError:
            try:
                attr = super(Wrapper, self).__getattribute__(attribute)
            except AttributeError:
                raise
        return attr
            
    def __setattr__(self, attribute, value):      
        try:
            wrapped_object = super(Wrapper, self).__getattribute__("wrapped_object")
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

    def __iter__(self):
        return self.wrapped_object
    
    def next(self): # python 2
        return next(self.wrapped_object)
        
    def __next__(self): # python 3
        return next(self.wrapped_object)

                                
class Process(Base):
    """a base process for processes to subclass from. Processes are managed
    by the system. The start method begins a process while the run method contains
    the actual code to be executed every frame."""
    
    defaults = defaults.Process
    
    def __init__(self, **kwargs):
        self.args = tuple()
        self.kwargs = dict()
        super(Process, self).__init__(**kwargs)
        if self.auto_start:
            args = (self.__class__.__name__, "start")
            options = {"component" : self,
                       "priority" : 0.0}
            Event(*args, **options).post()

    
    def start(self): # compatibility with multiprocessing.Process
        self.run()
        args = (self.__class__.__name__, "adjust_priority")
        options = {"component" : self,
                   "priority" : self.update_priority_interval}
   #     Event(*args, **options).post()
        
    def run(self):
        if self.target:
            self.target(*self.args, **self.kwargs)
        if self.recurring:        
            Event(self.instance_name, "run").post()
        else:
            Event(self.parent.instance_name, "delete", self).post()
 
    def adjust_priority(self):
        scaling_value = getattr(self, self.priority_scales_with, 1)
        scale_against = self.scale_against
        scale_function = getattr(scale_against, "__{0}__".format(self.scale_operator))
        priority = scale_function(scaling_value)
        print "calculated priority", priority, scale_against, scaling_value
        priority = max(priority, self.minimum_priority)
        print "after comparison to minimum", priority
        self.priority = min(priority, self.maximum_priority)
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

    def control_exchange(self, signal):
        print "doing control exchange with", str(signal)
        if callable(signal):
            print "got a signal"
            signal()
        else:
            return signal

    
# for vmlibrary.Machines
class Hardware_Device(Base):
    
    defaults = defaults.Hardware_Device
    
    def __init__(self, **kwargs):
        super(Hardware_Device, self).__init__(**kwargs)
        