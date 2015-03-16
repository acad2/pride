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
import sys
import traceback
import heapq
import importlib

import mpre
import mpre.metaclass
import defaults
import utilities
timer_function = utilities.timer_function


class Instruction(object):
    """ usage: Instruction(component_name, method_name, 
                           *args, **kwargs).execute(priority=priority)
                           
        Creates and executes an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds. 
        
        Instructions may be saved as an attribute of a component instead
        of continuously being instantiated. This allows the reuse of
        instruction objects. The same instruction object can be executed 
        any number of times.
        
        Note that Instructions must be executed to have any effect, and
        that they do not happen inline, even if priority is 0.0. 
        Because they do not execute in the current scope, the return value 
        from the method call is not available through this mechanism."""
              
    def __init__(self, component_name, method, *args, **kwargs):
        super(Instruction, self).__init__()
        self.created_at = timer_function()
        self.component_name = component_name
        self.method = method
        self.args = args
        self.kwargs = kwargs
        
    def execute(self, priority=0.0):
        heapq.heappush(Base.environment.Instructions, 
                      (timer_function() + priority, self))
            
    def __str__(self):
        args = self.args
        kwargs = self.kwargs
        number_of_formats = len(args)
        arg_string = ", ".join("{0}".format(args[index]) for index in xrange(number_of_formats))
        kwarg_string = ", ".join("{0}={1}".format(attr, value) for attr, value in kwargs.items())
        format_arguments = (self.component_name, self.method)#, arg_string, kwarg_string)
        return "Instruction {0}.{1}".format(*format_arguments)


class Alert(object):
    """ Utilizes a class as a namespace for holding global alert related
        configuration. This class is not instantiated anywhere.
        
        Contains the log_level and print_level global settings for alerts.
        The actual log file is Alert.log, which defaults to Alerts.log.
        The level_map associates alert level symbols with notification level"""
    log_level = 0
    print_level = 0
    log = open("Alerts.log", "a")
    level_map = {0 : "",
                'v' : "notification ",
                'vv' : "verbose notification ",
                'vvv' : "very verbose notification ",
                'vvvv' : "extremely verbose notification "}

            
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
    __metaclass__ = mpre.metaclass.Metaclass
    
    # A command line argument parser is generated automatically for
    # every Base class based upon the attributes contained in the
    # class defaults dictionary. Specific attributes can be modified
    # or ignored by specifying them here.
    parser_modifiers = {}
    parser_ignore = ("network_packet_size", "memory_size")
        
    # the default attributes an instance will initialize with.
    # storing them here and using the attribute_setter method
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
        
    def __new__(cls, *args, **kwargs):
        instance = super(Base, cls).__new__(cls)
                        
        # register name + number
        instance_number = instance.instance_number = cls.instance_count
        cls.instance_tracker[instance_number] = instance
        cls.instance_count += 1
        
        ending = str(instance_number) if instance_number else ''
        name = instance.instance_name = cls.__name__ + ending
        
        instance.environment.modify("Component_Resolve", (name, instance))

        return instance

    def __init__(self, **kwargs):
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
            memory_info = (mmap.mmap(-1, self.memory_size), [])            
            self.environment.modify("Component_Memory", 
                                   (self.instance_name, memory_info)) 
            
    def attribute_setter(self, **kwargs):
        """ usage: object.attribute_setter(attr1=value1, attr2=value2).
            
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
                    
        # instantiate the new object from a class object
        instance = instance_type(*args, **kwargs)

        self.add(instance)
        self.environment.modify("Parents", (instance, self.instance_name))
        
        return instance

    def delete(self):
        """usage: object.delete()
            
            Explicitly delete a component. This calls remove and
            attempts to clear out known references to the object so that
            the object can be collected by the python garbage collector"""
        assert not self.deleted
        self.deleted = True
        
        name = self.instance_name
                
        del self.instance_tracker[self.instance_number]
       
        # lists are mutatable during iteration, so copies have to be made
        for child_type, children in self.objects.items():
            children_names = [getattr(child, 'instance_name', child_type) for 
                              child in children]
            for _name in children_names:
                self.environment.modify("Component_Resolve", _name, "remove_item")
                                
      #  print "deleting references to", self
        names = [instance_name for instance_name in 
                 self.environment.References_To[self]]
                 
        for instance_name in names:
            instance = self.environment.Component_Resolve[instance_name]
            instance.remove(self)

        self.environment.modify("Component_Resolve", name, "remove_item")
        
        if self.memory_size:
            self.environment.modify("Component_Memory", name, 
                                    method="remove_item")
            
       # print "\nFinished deleting {}".format(self.instance_name)

    def remove(self, instance):
        """ Usage: object.remove(instance)
        
            Removes an instance from self.objects. Modifies object.objects
            and environment.References_To"""
        self.objects[instance.__class__.__name__].remove(instance)
        self.environment.References_To[instance].remove(self.instance_name)        
                
    def add(self, instance):
        """ usage: object.add(instance)

            Adds an object to the calling object. This performs
            reference bookkeeping so the added object can be 
            deleted successfully later."""        
        references = self.environment.References_To.get(instance, set())
        
        objects = self.objects
        instance_class = instance.__class__.__name__
        siblings = objects.get(instance_class, [])  
        
        if instance not in siblings:
            siblings.append(instance)
            objects[instance_class] = siblings
            references.add(self.instance_name)
            
            self.environment.modify("References_To", (instance, references))
                            
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
        an important message that should not and will never be suppressed."""

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
            need for an explicit reference to that object."""
        return getattr(self.environment.Component_Resolve[component_name], 
                       method_name)(*args, **kwargs)
                               
        
class Reactor(Base):
    """ usage: instance = Reactor(attribute=value, ...)
    
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
        attributes = self.__dict__.copy()
        attributes["_respond_with"] = [method.function.func_name for method in
                                       attributes["_respond_with"]]
        
        return attributes
        
    def __setstate__(self, state):
        state["_respond_with"] = [getattr(self, name) for name in
                                  state["_respond_with"]]
        self.__dict__.update(state)
        
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
            self.environment.modify("Parallel_Instructions", 
                                    component_name, "append")                
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
        return getattr(super(Wrapper, self).__getattribute__("wrapped_object"),
                       attribute)
                       
                       
class Proxy(Reactor):
    """ usage: Wrapper(wrapped_object=my_object) => wrapped_object
    
       Produces an instance that will act as the object it wraps and as an
       Reactor object simultaneously. This facilitates simple integration 
       with 'regular' python objects, providing them with monkey patches and
       the reaction/parallel_method/alert interfaces for very little effort.
       
       Proxy attributes are get/set on the underlying wrapped object first,
       and if that object does not have the attribute or it cannot be
       assigned, the action is performed on the proxy instead."""

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
        print "setting {} to {} on {}".format(attribute, value, self)
        super_object = super(Proxy, self)
        try:
            wrapped_object = super_object.__getattribute__("wrapped_object")
            super(type(wrapped_object), wrapped_object).__setattr__(attribute, value)
        except AttributeError:
            super_object.__setattr__(attribute, value)