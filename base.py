#   mpre.base - root inheritance objects
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
import sys
import traceback
import heapq
import importlib
import cPickle as pickle

import mpre
import mpre.metaclass
import mpre.utilities as utilities
import mpre.defaults as defaults

__all__ = ["Base", "Reactor", "Wrapper", "Proxy"]

class Base(object):
    """ usage: instance = Base(attribute=value, ...)
    
        The root inheritance object that provides many of the features
        of the runtime environment. An object that inherits from base will 
        possess these capabilities:
            
            - When instantiating, arbitrary attributes may be assigned
              via keyword arguments
              
            - The class includes a defaults attribute, which is a dictionary
              of name:value pairs. These pairs will be assigned as attributes
              to new instances; Any attribute specified via keyword argument
              will override a default
              
            - The flag parse_args=True may be passed to the call to 
              instantiate a new object. If so, then the metaclass
              generated parser will be used to interpret command
              line arguments. Only command line arguments that are
              in the class defaults dictionary will be assigned to 
              the new instance. Arguments by default are supplied 
              explicitly with long flags in the form --attribute value.
              Arguments assigned via the command line will override 
              both defaults and any keyword arg specified values. 
              Consult the parser defintion for further information,
              including using short/positional args and ignoring attributes.
              
            - The methods create/delete, and add/remove:
                - The create method returns an instantiated object and
                  calls add on it automatically. This performs book keeping
                  with the environment regarding references and parent information.
                - The delete method is used to explicitly destroy a component.
                  It calls remove internally to remove known locations
                  where the object is stored and update any tracking 
                  information in the environment
            
            - The alert method, which makes logging and statements 
              of varying verbosity simple and straight forward. Alerts
              also include options for callback methods and instructions
              
            - The method known as parallel_method. This method is used in a 
              similar capacity to Instruction objects, but the
              call happens immediately and the return value from the
              specified method is available
              
            - Decorator(s) and monkey patches may be specified via
              keyword argument to any method call. Note that this
              functionality does not apply to python objects
              builtin magic methods (i.e. __init__). The syntax
              for this is:
              
                - component.method(decorator='module.Decorator')
                - component.method(decorators=['module.Decorator', ...])
                - component.method(monkey_patch='module.Method')
              
              The usage of these does not permanently wrap/replace the
              method. The decorator/patch is only applied when specified.
            
            - Augmented docstrings. Information about class defaults
              and method names + argument signatures + method docstrings (if any)
              is included automatically. 
              
        Note that some features are facilitated by the metaclass. These include
        the argument parser, runtime decoration, and documentation.
        
        Instances of Base classes are counted and have an instance_name attribute.
        This is equal to type(instance).__name__ + str(instance_count). There
        is an exception to this; The first instance is number 0 and
        its name is simply type(instance).__name__, without 0 at the end.
        This name associates the instance to the instance_name in the
        mpre.environment.Component_Resolve. The instance_name is used
        for lookups in Instructions, parallel method calls, and reactions.
        
        Base objects can specify a memory_size attribute. If specified,
        the object will have a .memory attribute. This is a chunk of
        anonymous, contiguous memory of the size specified, provided
        by pythons mmap.mmap. This memory attribute can be useful because 
        it supports both the file-style read/write/seek interface and 
        string-style slicing"""
    __metaclass__ = mpre.metaclass.Metaclass#._metaclass
    
    # A command line argument parser is generated automatically for
    # every Base class based upon the attributes contained in the
    # class defaults dictionary. Specific attributes can be modified
    # or ignored by specifying them here.
    parser_modifiers = {}
    parser_ignore = ("network_packet_size", "memory_size")
        
    # the default attributes an instance will initialize with.
    # storing them here and using the set_attributes method
    # makes them modifiable at runtime and eliminates the need
    # to type out the usual self.attribute = value statements
    defaults = defaults.Base
    
    def _get_parent_name(self):
        return self.environment.Parents[self]
    parent_name = property(_get_parent_name)
    
    def _get_parent(self):
        environment = self.environment
        return environment.Component_Resolve[environment.Parents[self]]
    parent = property(_get_parent)
                       
    environment = mpre.environment
               
   # def __new__(cls, **kwargs):
   #     print "new new!"
    #    return super(Base, cls).__new__(cls)
        
    def __init__(self, **kwargs):
       #  self = super(Base, cls).__new__(cls, *args, **kwargs)
        # mutable datatypes (i.e. containers) should not be used inside the
        # defaults dictionary and should be set in the call to __init__
        self.objects = {}
        
        attributes = self.defaults.copy()
        attributes.update(kwargs)
        if kwargs.get("parse_args"):
            attributes.update(self.parser.get_options(attributes))
                
        self.set_attributes(**attributes)
        
        self.environment.add(self)
                
    def set_attributes(self, **kwargs):
        """ usage: object.set_attributes(attr1=value1, attr2=value2).
            
            Each key:value pair specified as keyword arguments will be
            assigned as attributes of the calling object. Keys are string
            attribute names and the corresponding values can be anything.
            
            This is called implicitly in __init__ for Base objects."""
        [setattr(self, attr, val) for attr, val in kwargs.items()]

    def create(self, instance_type, *args, **kwargs):
        """ usage: object.create("module_name.object_name", 
                                args, kwargs) => instance

            Given a type or string reference to a type, and arguments,
            return an instance of the specified type. The creating
            object will call .add on the created object, which
            performs reference tracking maintainence."""
        if not isinstance(instance_type, type):
            instance_type = utilities.resolve_string(instance_type)

        instance = instance_type(*args, **kwargs)

        self.add(instance)
        self.environment.modify("Parents", (instance, self.instance_name))        
        return instance

    def delete(self):
        """usage: object.delete()
            
            Explicitly delete a component. This calls remove and
            attempts to clear out known references to the object so that
            the object can be collected by the python garbage collector"""
        self.deleted = True
        self.environment.delete(self)

    def remove(self, instance):
        """ Usage: object.remove(instance)
        
            Removes an instance from self.objects. Modifies object.objects
            and environment.References_To"""
        self.objects[instance.__class__.__name__].remove(instance)
        self.environment.References_To[instance.instance_name].remove(self.instance_name)
        
    def add(self, instance):
        """ usage: object.add(instance)

            Adds an object to caller.objects[instance.__class__.__name__]"""   
        objects = self.objects
        instance_class = instance.__class__.__name__
        siblings = objects.get(instance_class, [])
        if instance not in siblings:
            siblings.append(instance)
            objects[instance_class] = siblings
            
            if hasattr(instance, "instance_name"):
                instance_name = instance.instance_name
                references_to = self.environment.References_To.get(instance_name, set())
                references_to.add(self.instance_name)
                self.environment.References_To[instance_name] = references_to            
     #   else:
       #     self.alert("Ignoring add of " + str(instance), level=0)
        #    raise type("AddException", (BaseException, ), 
          #             {"message" : "attempted to add an object that has already been added"})

            
    def alert(self, message="Unspecified alert message",
                    format_args=tuple(),
                    level=0,
                    callback=None):
        """usage: base.alert(message, format_args=tuple(), level=0, callback=None)

        Create an alert. Depending on the level given, the alert may be printed
        for immediate attention and/or logged quietly for later viewing.

        -message is a string that will be logged and/or displayed
        -format_args are any string formatting args for message.format()
        -level is an integer indicating the severity of the alert.
        -callback is an optional tuple of (function, args, kwargs) to be called when
         the alert is triggered

        alert severity is relative to Alert_Handler log_level and print_level;
        a lower number indicates a less verbose notification, while 0 indicates
        an important message that should not be suppressed."""
        if self.verbosity >= level:            
            message = (self.instance_name + ": " + message.format(*format_args) if
                       format_args else self.instance_name + ": " + message)

            return self.parallel_method("Alert_Handler", "alert",
                                        message,
                                        level, callback)            
                        
    def parallel_method(self, component_name, method_name, *args, **kwargs):
        """ usage: base.parallel_method(component_name, method_name, 
                                       *args, **kwargs) 
                                       => component.method(*args, **kwargs)
                  
            Used to call the method of an existing external component.
           
            -component_name is a string of the instance_name of the component
            -method_name is a string of the method to be called
            -arguments and keyword arguments for the method may optionally
             be supplied after the component_name and method_name
             
            The method is called immediately and the return value of the
            method is made available as the return value of parallel_method.
            
            parallel_method allows for the use of an object without the
            need for a reference to that object in the current scope."""
        return getattr(self.environment.Component_Resolve[component_name], 
                       method_name)(*args, **kwargs)
                               
    def __getstate__(self):
        return self.__dict__.copy()
        
    def __setstate__(self, state):
        self.set_attributes(**state)
        self.environment.add(self)
        return self
        
    def update(self, source_file=None):
        """usage: base.update() => updated_base
        
           Reloads the module that defines base and returns an updated instance. 
           The environment is updated with the new component information. Further
           references to the object via instance_name will be directed to the
           new, updated object. Attributes of the original object will be assigned
           to the new, updated object.
           
           4/8/15: not solid in terms of object deletion yet. leaks ~250kb per update"""
        self.alert("Updating", level='v')        
        class_mro = self.__class__.__mro__[:-1]
        class_base = self.__class__.__mro__[-1]
        required_modules = []        
        preserved_modules = {}
        
        for cls in reversed(class_mro):
            module_name = cls.__module__
            current_module = sys.modules.pop(module_name)
            preserved_modules[module_name] = current_module
            importlib.import_module(module_name)
            required_modules.append(sys.modules[module_name])

        class_base = getattr(required_modules[-1], self.__class__.__name__)
        # breaks if this is not done. maybe modules are garbage collected otherwise?
        class_base.required_modules = required_modules
        
        new_self = class_base.__new__(class_base)
                
        # a mini replacement __init__
        attributes = new_self.defaults.copy()
        new_self.set_attributes(**attributes)
        self.environment.add(new_self)        
     
        stats = self.__dict__
        self.environment.replace(self, new_self)
        new_self.set_attributes(**stats)
        sys.modules.update(preserved_modules)
        return new_self
        

class Reactor(Base):
    """ usage: Reactor(attribute=value, ...) => reactor_instance
    
        Adds reaction framework on top of a Base object. 
        Reactions are event triggered chains of method calls
        
        This class is a recent addition and may not be completely
        final in it's api and/or implementation.
        TODO: add transparent remote reaction support!"""
    
    defaults = defaults.Reactor
    
    def __init__(self, **kwargs):
        super(Reactor, self).__init__(**kwargs)        
        self._respond_with = []
    
    def __getstate__(self):
        attributes = super(Reactor, self).__getstate__()
        attributes["_respond_with"] = [method.function.func_name for method in
                                       attributes["_respond_with"]]
        return attributes
        
    def __setstate__(self, state):
        state["_respond_with"] = [getattr(self, name) for name in
                                  state["_respond_with"]]
        super(Reactor, self).__setstate__(state)
        return self
        
    def reaction(self, component_name, message,
                 _response_to="None",
                 scope="local"):
        """Usage: component.reaction(target_component, message, 
                                    [scope='local'])
        
            calls a method on target_component. message is a string that
            contains the method name followed by arguments separate by
            spaces. 
            
            The scope keyword specifies the location of the expected
            component, and the way the component will be reached.
            
            When scope is 'local', the component is the component that resides
            under the specified name in environment.Component_Resolve. This
            reaction happens immediately.
            
            The following is not implemented as of 3/1/2015:
            When scope is 'global', the component is a parallel reactor
            and the message will be written to memory. This reaction is
            scheduled among worker processes.
            
            When scope is "network", the component is a remote reactor
            on a remote machine and the message will be sent via a reaction 
            with the service proxy, which sends the request via the network.
            
            If scope is 'network', then component_name is a tuple containing
            the component name and a tuple containing the host address port"""
        if scope is 'local':
            self.parallel_method(component_name, "react", 
                                 self.instance_name, message)
       
        elif scope is 'global':
            raise NotImplementedError
            memory, pointers = self.environment.Component_Memory[component_name]
                                                              
            memory.write(packet)
            pointers.append((self.instance_name, memory.tell()))
            
        elif scope is 'network':
            raise NotImplementedError
            component_name, host_info = component_name
            self.parallel_method("Service_Proxy", "send_to", component_name, 
                               host_info, self.instance_name, message)
                    
    def react(self, sender, packet):        
        command, value = packet.split(" ", 1)
                                   
        self.alert("handling response {} {}",
                   [command, value[:32]],
                   level='vv')
        
        method = (self._respond_with.pop(0) if self._respond_with else
                  getattr(self, command))
                  
        response = method(sender, value)
        
        if response:                                
            self.alert("Sending response; To: {}, Response: {}",
                       [sender, response],
                       level='vvv')
            self.reaction(sender, response)                    
    
    def respond_with(self, method):
        """ usage: self.respond_with(method)
        
            Specifies what method should be called when the component
            specified by a reaction returns its response."""
        self._respond_with.append(method)
        

class Wrapper(Reactor):
    """ A wrapper to allow python objects to function as a Reactor.
        The attributes on this wrapper will overload the attributes
        of the wrapped object. """
    def __init__(self, **kwargs):
        self.wrapped_object = kwargs.pop("wrapped_object", None)
        super(Wrapper, self).__init__(**kwargs)
                
    def __getattr__(self, attribute):
        return getattr(self.wrapped_object, attribute)
                       
                       
class Proxy(Reactor):
    """ usage: Proxy(wrapped_object=my_object) => proxied_object
    
       Produces an instance that will act as the object it wraps and as an
       Reactor object simultaneously. This facilitates simple integration 
       with 'regular' python objects, providing them with monkey patches and
       the reaction/parallel_method/alert interfaces for very little effort.
       
       Proxy attributes are get/set on the underlying wrapped object first,
       and if that object does not have the attribute or it cannot be
       assigned, the action is performed on the proxy wrapper instead."""

    def __init__(self, **kwargs):
        wraps = super(Proxy, self).__getattribute__("wraps")
        try:
            wrapped_object = kwargs.pop("wrapped_object")
        except KeyError:
            pass
        else:
            wraps(wrapped_object)
        super(Proxy, self).__init__(**kwargs)

    def wraps(self, obj, set_defaults=False):
        """ usage: wrapper.wraps(object)
            
            Makes the supplied object the object that is wrapped
            by the calling wrapper. If the optional set_defaults
            attribute is True, then the wrapped objects class
            defaults will be applied."""
        set_attr = super(Proxy, self).__setattr__
        if set_defaults:
            for attribute, value in self.defaults.items():
                set_attr(attribute, value)
        set_attr("wrapped_object", obj)

    def __getattribute__(self, attribute):
        try:
            wrapped_object = super(Proxy, self).__getattribute__("wrapped_object")
            value = super(type(wrapped_object), wrapped_object).__getattribute__(attribute)
        except AttributeError:
            value = super(Proxy, self).__getattribute__(attribute)
        return value

    def __setattr__(self, attribute, value):
        super_object = super(Proxy, self)
        try:
            wrapped_object = super_object.__getattribute__("wrapped_object")
            super(type(wrapped_object), wrapped_object).__setattr__(attribute, value)
        except AttributeError:
            super_object.__setattr__(attribute, value)