""" Contains The root inheritance objects that provides many of the features
    of the runtime environment. An object that inherits from mpre.base.Base will 
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
          of varying verbosity simple and straight forward.
          
        - parallel_method calls. This is the primary concurreny mechanism 
          and is used in a similar capacity to Instruction objects.
          The difference is that the call happens immediately and the return 
          value from the specified method is available in the calling scope
          
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
    mpre.environment.Component_Resolve. The instance_name can be used to reference
    the object from any scope, as long as the component exists."""
import mmap
import sys
import traceback
import heapq
import importlib
import operator
import inspect
import hashlib
try:
    import cPickle as pickle
except ImportError:
    import pickle
       
import mpre
import mpre.metaclass
import mpre.persistence as persistence
import mpre.utilities as utilities

import mpre.importers as importers
import mpre.module_utilities as module_utilities
from mpre.errors import *

__all__ = ["DeleteError", "AddError", "Base", "Reactor", "Wrapper", "Proxy"]


class Base(object):

    __metaclass__ = mpre.metaclass.Metaclass
    
    # A command line argument parser is generated automatically for
    # every Base class based upon the attributes contained in the
    # class defaults dictionary. Specific attributes can be modified
    # or ignored by specifying them here.
    parser_modifiers = {}
            
    # the default attributes new instances will initialize with.
    defaults = {"verbosity" : '',
                "_deleted" : False,
                "replace_reference_on_load" : True}
    
    def _get_parent_name(self):
        return self.environment.Parents[self]
    parent_name = property(_get_parent_name)
    
    def _get_parent(self):
        environment = self.environment
        return environment.Component_Resolve[environment.Parents[self]]
    parent = property(_get_parent)

    environment = mpre.environment
        
    def __init__(self, **kwargs):
       #  self = super(Base, cls).__new__(cls, *args, **kwargs)
        # mutable datatypes (i.e. containers) should not be used inside the
        # defaults dictionary and should be set in the call to __init__                
        attributes = self.defaults.copy()
        attributes["objects"] = {}
        attributes.update(kwargs)
        if kwargs.get("parse_args"):
            attributes.update(self.parser.get_options(attributes))        
        
        self.set_attributes(**attributes)        
        self.environment.add(self)
        self._added = True
        
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
            performs reference tracking maintainence. 
            
            Use of the create method over direct instantiation can allow even 
            'regular' python objects to have a reference and be usable via parallel_methods 
            and Instruction objects."""
        if not isinstance(instance_type, type):
            instance_type = utilities.resolve_string(instance_type)
        instance = instance_type(*args, **kwargs)

        if not getattr(instance, "_added", False):
            self.environment.add(instance)
        self.add(instance)
        self.environment.Parents[instance] = self.instance_name
        return instance

    def delete(self):
        """usage: object.delete()
            
            Explicitly delete a component. This calls remove and
            attempts to clear out known references to the object so that
            the object can be collected by the python garbage collector"""
        if self._deleted:
            raise DeleteError("{} has already been deleted".format(self.instance_name))
        self.environment.delete(self)
        self._deleted = True
        
    def remove(self, instance):
        """ Usage: object.remove(instance)
        
            Removes an instance from self.objects. Modifies object.objects
            and environment.References_To."""
        self.objects[instance.__class__.__name__].remove(instance)
        self.environment.References_To[instance.instance_name].remove(self.instance_name)
        
    def add(self, instance):
        """ usage: object.add(instance)

            Adds an object to caller.objects[instance.__class__.__name__] and
            performs bookkeeping operations for the environment."""   
        
        objects = self.objects
        instance_class = instance.__class__.__name__
        siblings = objects.get(instance_class, [])#set())
        if instance in siblings:
            raise AddError
        #siblings.add(instance)
        siblings.append(instance)
        objects[instance_class] = siblings      
                    
        instance_name = self.environment.Instance_Name[instance]
        try:
            self.environment.References_To[instance_name].add(self.instance_name)
        except KeyError:
            self.environment.References_To[instance_name] = set((self.instance_name, ))      
            
    def alert(self, message="Unspecified alert message", format_args=tuple(), level=0):
        """usage: base.alert(message, format_args=tuple(), level=0)

        Display/log a message according to the level given. The alert may be printed
        for immediate attention and/or logged quietly for later viewing.

        -message is a string that will be logged and/or displayed
        -format_args are any string formatting args for message.format()
        -level is an integer indicating the severity of the alert.

        alert severity is relative to Alert_Handler log_level and print_level;
        a lower verbosity indicates a less verbose notification, while 0 indicates
        a message that should not be suppressed. log_level and print_level
        may passed in as command line arguments to globally control verbosity."""
        if self.verbosity >= level:            
            message = (self.instance_name + ": " + message.format(*format_args) if
                       format_args else self.instance_name + ": " + message)
            return self.parallel_method("Alert_Handler", "_alert", message, level)            
                        
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
        self.on_load(state)
              
    def __str__(self):
        return self.instance_name
        
    def save(self, attributes=None, _file=None):
        """ usage: base.save([attributes], [_file])
            
            Saves the state of the calling objects __dict__. If _file is not specified,
            a pickled stream is returned. If _file is specified, the stream is written
            to the supplied file like object via pickle.dump.
            
            The attributes argument, if specified, should be a dictionary containing 
            the attribute:value pairs to be pickled instead of the objects __dict__.
            
            If the calling object is one that has been created via the update method, the 
            returned state will include any required source code to rebuild the object."""
        attributes = self.__getstate__()
        objects = attributes.pop("objects", {})
        saved_objects = attributes["objects"] = {}
        found_objects = []
        for component_type, values in objects.items():
            saved_objects[component_type] = new_values = []
            for value in sorted(values, key=operator.attrgetter("instance_name")):
                if hasattr(value, "save"):     
                    found_objects.append(value)
                    new_values.append(value.save())
                    
        attribute_type = attributes["_attribute_type"] = {}
        for key, value in attributes.items():
            if value in found_objects:
                attributes[key] = value.instance_name
                attribute_type[key] = "reference"
            elif hasattr(value, "save"):
                attributes[key] = value.save()
                attribute_type[key] = "saved"      
        return persistence.save(self, attributes, _file)    
            
    @staticmethod
    def load(attributes='', _file=None):
        """ Loads and instance from a bytestream or file produced by save. This
            calls persistence.load but may look syntatically nicer."""
        assert attributes or _file
        new_self, attributes = persistence.load(attributes, _file)
   
        saved_objects = attributes["objects"]
        objects = attributes["objects"] = {}
        
        for instance_type, saved_instances in saved_objects.items(): 
            objects[instance_type] = [Base.load(instance) for instance in saved_instances]
            
        attribute_modifier = attributes.pop("_attribute_type")
        for key, value in attributes.items():
            modifier = attribute_modifier.get(key, '')
            if modifier == "reference":
                attributes[key] = mpre.component[value]
            elif modifier == "save":
                attributes[key] = Base.load(value) # may need to be pickle.dumps(value)
                
        new_self.on_load(attributes)
        return new_self
        
    def on_load(self, attributes):
        """ usage: base.on_load(attributes)
        
            Implements the behavior of an object after it has been loaded. This method 
            may be extended by subclasses to customize functionality for instances created
            by the load method."""                
        self.set_attributes(**attributes)
        self.environment.add(self)
        if self.replace_reference_on_load and self.instance_name != attributes["instance_name"]:
            self.environment.replace(attributes["instance_name"], self)
        self.alert("Loaded", level='v')
        
    def update(self):
        """usage: base_instance.update() => updated_base
        
           Reloads the module that defines base and returns an updated instance. The
           old component is replaced by the updated component in the environment.
           Further references to the object via instance_name will be directed to the
           new, updated object. Attributes of the original object will be assigned
           to the updated object."""
        self.alert("Updating", level='v') 
        class_base = utilities.updated_class(type(self))
        class_base._required_modules.append(self.__class__.__name__)        
        new_self = class_base.__new__(class_base)
                
        # a mini replacement __init__
        attributes = new_self.defaults.copy()
        attributes["_required_modules"] = class_base._required_modules
        new_self.set_attributes(**attributes)
        self.environment.add(new_self)        
        
        attributes = self.__dict__
        self.environment.replace(self, new_self)
        new_self.set_attributes(**attributes)
        return new_self
                
        
class Reactor(Base):
    """ usage: Reactor(attribute=value, ...) => reactor_instance
    
        Adds reaction framework on top of a Base object. 
        Reactions are event triggered chains of method calls
        
        This class is a recent addition and is far from final in it's api and
        implementation. """
    
    defaults = Base.defaults.copy()
    
    def __init__(self, **kwargs):
        super(Reactor, self).__init__(**kwargs)        
        self._respond_with = []
                
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
       
        """elif scope is 'global':
            raise NotImplementedError
            memory, pointers = self.environment.Component_Memory[component_name]
                                                              
            memory.write(packet)
            pointers.append((self.instance_name, memory.tell()))
            
        elif scope is 'network':
            raise NotImplementedError
            component_name, host_info = component_name
            self.parallel_method("Service_Proxy", "send_to", component_name, 
                               host_info, self.instance_name, message)"""
                    
    def react(self, sender, packet):        
        command, value = packet.split(" ", 1)
                                   
        self.alert("handling response {} {}",
                   [command, value[:32]],
                   level='vv')
        
        method = (getattr(self, self._respond_with.pop(0)) if 
                  self._respond_with else getattr(self, command))                  
        response = method(sender, value)
        
        if response:                                
            self.alert("Sending response; To: {}, Response: {}",
                       [sender, response],
                       level='vvv')
            self.reaction(sender, response)                    
    
    def respond_with(self, method_name):
        """ usage: self.respond_with(method)
        
            Specifies what method should be called when the component
            specified by a reaction returns its response."""
        self._respond_with.append(method_name)
        

class Wrapper(Reactor):
    """ A wrapper to allow 'regular' python objects to function as a Reactor.
        The attributes on this wrapper will overload the attributes
        of the wrapped object. Any attributes not present on the wrapper object
        will be gotten from the underlying wrapped object. This class
        acts primarily as a wrapper and secondly as the wrapped object."""
     
    defaults = Reactor.defaults.copy()
    defaults.update({"wrapped_object" : None})
    wrapped_object_name = ''
    
    def __init__(self, **kwargs):
        super(Wrapper, self).__init__(**kwargs)
        if self.wrapped_object_name:
            setattr(self, self.wrapped_object_name, self.wrapped_object)
            
    def __getattr__(self, attribute):
        return getattr(self.wrapped_object, attribute)        
                       
    def wraps(self, _object):
        self.wrapped_object = _object
        
        
class Proxy(Reactor):
    """ usage: Proxy(wrapped_object=my_object) => proxied_object
    
       Produces an instance that will act as the object it wraps and as an
       Reactor object simultaneously. The object will act primarily as
       the wrapped object and secondly as a proxy object. This means that       
       Proxy attributes are get/set on the underlying wrapped object first,
       and if that object does not have the attribute or it cannot be
       assigned, the action is performed on the proxy instead. This
       prioritization is the opposite of the Wrapper class."""

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