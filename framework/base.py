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
#import dill
from Queue import Queue
from weakref import proxy, ref

import defaults

Component_Memory = {} 
Component_Resolve = {}

    
class Event(object):
    
    events = Queue()
            
    def __init__(self, component_name, method, *args, **kwargs):
        super(Event, self).__init__()
        self.component_name = component_name
        self.method = method # any method can be supplied
        self.args = args # any arguments can be supplied
        self.kwargs = kwargs # any keyword arguments can be supplied
        self.created_at = time.clock()
        
        try:
            self.component = kwargs.pop("component")
        except KeyError:
            self.component = None
        try:
            self.priority = kwargs.pop("priority")
        except KeyError:
            self.priority = 16 # 16/1000 is about 60 fps not implemented
               
    def post(self):
        #vv: print "posted", self, self.args, self.kwargs
        #Component_Memory["Event_Handler0"].write(dill.dumps(self) + "delimiter")
        Event.events.put(self)
        
    def __str__(self):
        return "%s_Event: %s" % (self.component_name, self.method)
        
    def execute_code(self):    
        call = getattr(self.component, self.method)
        call(*self.args, **self.kwargs)   
 
    @staticmethod
    def _get_events():
        """Used by the event handler to acquire a frame of events"""
        events = Event.events
        Event.events = Queue()
        return events 
        
        
class Docstring(object):
    
    def __init__(self):
        super(Docstring, self).__init__()
        
    def __get__(self, instance, _class):
        options_text = '\n Default values for newly created instances:\n'     
        try: # gather the default attribute names and values
            options = ""
            for key, value in _class.defaults.items():
                options += " \t%s\t%s\n" % (key, value)
            if not options:
                options_text = "\n No defaults are assigned to new instances\n"
            else:
                options_text += options
        except KeyError: # does not have defaults
            options_text = "\n No class.defaults detected\n"
        docstring = "%s:\n" % _class.__name__
        class_docstring = getattr(_class, "__doc")
        docstring += "\t"+class_docstring+"\n"+options_text+"\n"
        docstring += " This object defines the following public methods:\n"
        count = 0
        found = False
        uses_decorator = False
        for attribute_name in _class.__dict__.keys():
            if "_" != attribute_name[0]:
                attribute = getattr(_class, attribute_name)
                if callable(attribute):
                    found = True
                    count += 1
                    count_string = str(count)        
                    docstring += " \t"+count_string+". "+attribute_name+", which uses the following argument specification:\n"
                    argspec = inspect.getargspec(attribute)
                    if argspec.args:
                        docstring += " \t\tRequired arguments: " + str(argspec.args) + "\n"
                    if argspec.defaults:
                        docstring += " \t\tDefault arguments: " + str(argspec.defaults) + "\n"
                    if argspec.varargs:
                        docstring += " \t\tVariable positional arguments: " + str(argspec.varargs)+ "\n"
                    if argspec.keywords:
                        docstring += " \t\tKeyword arguments: " + str(argspec.keywords) + "\n"""
        if not found:
            docstring += " \tNo public methods defined\n"
        docstring += "\n This objects method resolution order/class hierarchy is:\n \t"
        docstring += str(_class.__mro__)
        return docstring
                

class Metaclass(type):
    """Includes class.defaults attribute/values in docstrings."""
    
    def __new__(cls, name, bases, attributes):
        try:
            docstring = attributes["__doc__"]
        except KeyError:
            docstring = "No docstring found. Only introspected information available\n"
        attributes["__doc"] = docstring
        attributes["__doc__"] = Docstring()
        new_class = type.__new__(cls, name, bases, attributes)
        return new_class
            

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
        
    # hotkeys should be pygame.locals.key_constant : eventlibrary.Event pairs
    hotkeys = {}
        
    def __init__(self, **kwargs):
        # mutable datatypes (i.e. containers) should not be used inside the
        # defaults dictionary and should be set in the __init__, like so
        self.objects = {}
        super(Base, self).__init__()
        attributes = dict(self.defaults.items())
        if kwargs:
            attributes.update(kwargs)
        self.attribute_setter(**attributes)     
    
    def __getattribute__(self, attribute):  
        value = super(Base, self).__getattribute__(attribute)
        if "__" not in attribute and callable(value):
            value = Runtime_Decorator(value)
        return value
        
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
            kwargs["parent"] = proxy(self)
            kwargs["parent_weakref"] = ref(self)
            
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
            #print "attempting to instantiate", instance_type, args, kwargs
            instance = instance_type(*args, **kwargs)
        except:
            raise # uncomment when developing new things!
            self.warning("Failed to instantiate %s, wrapping" % instance_type, "Notification:")
            instance = instance_type(*args)
            instance = Wrapper(instance, **kwargs)
        instance.added_to = []
        self.add(instance)
        class_name = instance.__class__.__name__
        number = self.objects[class_name].index(instance)
        name = class_name + str(number)
        instance._instance_number = number
        instance._instance_name = name
        memory = mmap.mmap(-1, instance.memory_size)        
        Component_Resolve[name] = instance
        Component_Memory[name] = memory        
        return instance
        
    def add(self, instance):
        """usage: object.add(other_object)

        adds an already existing object to the instances' class name entry in parent.objects.
        """
        
        if not hasattr(instance, "parent"):
            instance.parent = self # is a reference problem without stm in place
        instance.added_to.append(self)
        #print "adding %s to %s.objects[%s]" % (instance, instance.parent, instance.__class__.__name__)
        try:
            self.objects[instance.__class__.__name__].append(instance)
        except KeyError:
            self.objects[instance.__class__.__name__] = [instance]
        
    def delete(self, *args):
        """usage: object.delete() or object.delete(child)
        
        currently does not always function as intended. don't rely on it!"""
        import gc
        if not args:     
            for child in self.get_children():
                child.delete()
            for instance in self.added_to:
                instance.objects[self.__class__.__name__].remove(self)
        else:
            for instance in args:
                self.objects[instance.__class__.__name__].remove(instance)

    def send_to(self, component_name, message):
        Component_Memory[component_name].write(message+"delimiter")
        
    def read_messages(self):
        memory = Component_Memory[self._instance_name]
        memory.seek(0)
        data = memory.read(self.memory_size)
        memory.seek(0)
        if data.replace("\x00", ""):
            size = len(data)   
            messages = data.split("delimiter")[:1]
            memory.write("\x00"*size)
            memory.seek(0)
        else:
            messages = []        
        return messages
        
    def warning(self, message="Error_Code", level="Warning", callback=None, callback_event=None):
        """usage: object.warning(Message, level, callback)
        
        print a warning message to the console. the message will be prefixed by
        the severity of the error, which can be specified via the level argument.
        a callback_event can be supplied, which should be an eventlibrary.Event"""
        print level, message
        
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
    

#@functools.wraps # metadata would be nice...      
class Wrapper(Base):
    """a class that will act as the object it wraps and as a base
    object simultaneously."""
       
    def __init__(self, wrapped_object=None, **kwargs):
        attributes = {"wrapped_object" : wrapped_object, "objects" : {}}
        default_kwargs = super(Wrapper, self).__getattribute__("defaults")
        if default_kwargs:
            attributes.update(default_kwargs)
        if kwargs:
            attributes.update(kwargs)
        super(Wrapper, self).attribute_setter(**attributes)
                       
    def _get_wrapper_attribute(self, attribute):
        return super(Wrapper, self).__getattribute__(attribute)

    def __getattribute__(self, attribute): 
        wrapped_object = super(Wrapper, self).__getattribute__("wrapped_object")
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
            event = Event(self.__class__.__name__, "start")
            event.component = self
            event.post()
    
    def start(self): # compatibility with multiprocessing.Process
        self.run()
            
    def run(self):
        if self.target:
            self.target(*self.args, **self.kwargs)
        if self.recurring:        
            Event(self._instance_name, "run").post()
        else:
            Event(self.parent._instance_name, "delete", self).post()
 
 
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

        
# for machinelibrary.Machines
class Hardware_Device(Base):
    
    defaults = defaults.Hardware_Device
    
    def __init__(self, **kwargs):
        super(Hardware_Device, self).__init__(**kwargs)
        

class Runtime_Decorator(object):
    """provides the ability to call a function with a decorator specified via
    keyword argument.
    
    example: my_function(my_argument1, decorator="decoratorlibary.Tracer")"""
    
    def __init__(self, function):
        self.function = function
            
    def __call__(self, *args, **kwargs):

        if kwargs.has_key("context_manager"):
            module_name, context_manager_name = self._resolve_string(kwargs.pop("context_manager"))
            module = self._get_module(module_name)
            context_manager = getattr(module, context_manager_name)
            with context_manager():
                self.function(*args, **kwargs)
                
        if kwargs.has_key("monkey_patch"):
            module_name, patch_name = self._resolve_string(kwargs.pop("monkey_patch"))
            module = self._get_module(module_name)
            monkey_patch = getattr(module, patch_name)
            return monkey_patch(self.function.im_self, *args, **kwargs)
            
        if kwargs.has_key('decorator'):
            decorator_type = str(kwargs['decorator']) # string value of kwargs['decorator']
            
            module_name, decorator_name = self._resolve_string(decorator_type)
            decorator = self._get_decorator(decorator_name, module_name)
            wrapped_function = decorator(self.function)
            del kwargs['decorator']
            return wrapped_function(*args, **kwargs)

        elif kwargs.has_key('decorators'):
            decorators = []

            for item in kwargs['decorators']:
                module_name, decorator_name = self._resolve_string(item)
                decorator = self._get_decorator(decorator_name, module_name)
                decorators.append(decorator)

            wrapped_function = self.function
            for item in reversed(decorators):
                wrapped_function = item(wrapped_function)
            del kwargs['decorators']
            return wrapped_function(*args, **kwargs)

        else:
            return self.function(*args, **kwargs)

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