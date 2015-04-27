import sys
import os
import types
defaults_source = r'''
#   mpf.defaults - config file - contains attributes:values for new instances
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
import struct
import socket
import os

NO_ARGS = tuple()
NO_KWARGS = dict()

if "__file__" not in globals():
    FILEPATH = os.getcwd()
else:
    FILEPATH = os.path.split(__file__)[0]

# Base
MANUALLY_REQUEST_MEMORY = 0
DEFAULT_MEMORY_SIZE = 4096

# anonymous memory passes -1  as the file descriptor to pythons mmap.mmap.
# persistent memory opens the file instance.instance_name and opens an
# mmap.mmap with that files file descriptor
ANONYMOUS = -1
PERSISTENT = 0
Base = {"memory_size" : DEFAULT_MEMORY_SIZE,
"memory_mode" : ANONYMOUS,
"verbosity" : '',
"deleted" : False}

Reactor = Base.copy()

Process = Base.copy()
Process.update({"auto_start" : True,
"priority" : .04})

# vmlibrary

Processor = Process.copy()
Processor.update({"running" : True,
"auto_start" : False})

User_Input = Process.copy()

# network

Socket = Base.copy()
Socket.update({"blocking" : 0,
"timeout" : 0,
"add_on_init" : True,
"network_packet_size" : 32768,
"memory_size" : 0,
"network_buffer" : '',
"interface" : "0.0.0.0",
"port" : 0,
"connection_attempts" : 10,
"bind_on_init" : False,
"closed" : False,
"_connecting" : False,
"added_to_network" : False})

Tcp_Socket = Socket.copy()
Tcp_Socket.update({"socket_family" : socket.AF_INET,
"socket_type" : socket.SOCK_STREAM})

Server = Tcp_Socket.copy()
Server.update({"port" : 80,
"backlog" : 50,
"name" : "",
"reuse_port" : 0,
"Tcp_Socket_type" : "network.Tcp_Socket",
"share_methods" : ("on_connect", "client_socket_recv", "client_socket_send")})

Tcp_Client = Tcp_Socket.copy()
Tcp_Client.update({"ip" : "",
"port" : 80,
"target" : tuple(),
"as_port" : 0,
"timeout_notify" : True,
"auto_connect" : True,
"bad_target_verbosity" : 0}) # alert verbosity when trying to connect to bad address
del Tcp_Client["interface"]

Udp_Socket = Socket.copy()
Udp_Socket.update({"bind_on_init" : True})
del Udp_Socket["connection_attempts"]

# only addresses in the range of 224.0.0.0 to 230.255.255.255 are valid for IP multicast
Multicast_Beacon = Udp_Socket.copy()
Multicast_Beacon.update({"packet_ttl" : struct.pack("b", 127),
"multicast_group" : "224.0.0.0",
"multicast_port" : 1929})

Multicast_Receiver = Udp_Socket.copy()
Multicast_Receiver.update({"address" : "224.0.0.0"})

Connection_Manager = Process.copy()
Connection_Manager.update({"auto_start" : False})

Network = Process.copy()
Network.update({"handle_resends" : False,
"number_of_sockets" : 0,
"priority" : .01,
"update_priority" : 5,
"_updating" : False,
"auto_start" : False})

# network2
Network_Service = Udp_Socket.copy()

Authenticated_Service = Base.copy()
Authenticated_Service.update({"database_filename" : ":memory:",
"login_message" : 'login success',
"hash_rounds" : 100000})

Authenticated_Client = Base.copy()
Authenticated_Client.update({"email" : '',
"username" : "",
"password" : '',
"target" : "Authenticated_Service"})

File_Service = Base.copy()
File_Service.update({"network_packet_size" : 16384,
"mmap_threshold" : 16384,
"timeout_after" : 15})

Download = Base.copy()
Download.update({"filesize" : 0,
"filename" :'',
"filename_prefix" : "Download",
"download_in_progress" : False,
"network_packet_size" : 16384,
"timeout_after" : 15})

 # Metapython
JYTHON = "java -jar jython.jar"
PYPY = "pypy"
CPYTHON = "python"
DEFAULT_IMPLEMENTATION = CPYTHON

Shell = Authenticated_Client.copy()
Shell.update({"email" : '',
"username" : "root",
"password" : "password",
"prompt" : ">>> ",
"startup_definitions" : '',
"target" : "Interpreter_Service"})

Interpreter_Service = Authenticated_Service.copy()
Interpreter_Service.update({"copyright" : 'Type "help", "copyright", "credits" or "license" for more information.'})

Alert_Handler = Reactor.copy()
Alert_Handler.update({"log_level" : 0,
                      "print_level" : 0,
                      "log_name" : "Alerts.log"})
                      
Metapython = Reactor.copy()
Metapython.update({"command" : os.path.join(FILEPATH, "shell_launcher.py"),
"implementation" : DEFAULT_IMPLEMENTATION,
"environment_setup" : ["PYSDL2_DLL_PATH = C:\\Python27\\DLLs"],
"interface" : "0.0.0.0",
"port" : 40022,
"prompt" : ">>> ",
"_suspended_file_name" : "suspended_interpreter.bin",
"copyright" : 'Type "help", "copyright", "credits" or "license" for more information.',
"priority" : .04,
"interpreter_enabled" : True,
"startup_definitions" : \
"""Instruction('Metapython', 'create', 'userinput.User_Input').execute()
Instruction("Metapython", "create", "network.Network").execute()"""})
#"help" : "Execute a python script or launch a live metapython session"})
'''

metaclass_source = r'''
import sys
import argparse
import types
import functools
import ast
import inspect
import utilities
from copy import copy

class Docstring(object):
    """ A descriptor object used by the Documented metaclass. Augments
        instance docstrings with introspected information"""
    def __init__(self):
        super(Docstring, self).__init__()

    def __get__(self, instance, _class):
        _object = instance if instance else _class
        return utilities.documentation(_object)
        
        
class Documented(type):
    """ A metaclass that uses the Docstring object to supply
        abundant documentation for classes"""
    def __new__(cls, name, bases, attributes):
        cls.make_docstring(attributes)
        return super(Documented, cls).__new__(cls, name, bases, attributes)
        
    @staticmethod
    def make_docstring(attributes):
        attributes["__doc"] = attributes.get("__doc__", "No docstring found")
        attributes["__doc__"] = Docstring()
        

class Method_Hook(type):
    """ Provides a hook on all methods for the new class. This metaclass
        uses this hook to wrap each method in a Runtime_Decorator."""
        
    def __new__(cls, name, bases, attributes):        
        new_class = super(Method_Hook, cls).__new__(cls, name, bases, attributes)
        Method_Hook.decorate(new_class)
        return new_class
        
    @staticmethod
    def decorate(new_class):
        for key, value in new_class.__dict__.items():
            if key[0] != "_" and callable(value):
                bound_method = types.MethodType(Runtime_Decorator(value), 
                                                None, 
                                                new_class)
                setattr(new_class, key, bound_method)
        return new_class        
        
        
class Runtime_Decorator(object):
    """ Provides the ability to call a method with a decorator, decorators,
        or monkey patch specified via keyword argument. This decorator
        inherits from object and utilizes the Documented metaclass.

        usage: wrapped_method(my_argument, decorator="decorators.Tracer")"""
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
            
    """def _handle_context_manager(self, context_manager):
        raise NotImplementedError
        if isinstance(context_manager, str):
            context_manager = utilities.resolve_string(context_manager)
        return context_manager   

        with context_manager():
            result = self.function(*args, **kwargs)
        return result"""

    def _handle_monkey_patch(self, monkey_patch):
        if isinstance(monkey_patch, str):
            monkey_patch = utilities.resolve_string(monkey_patch)
        try:
            monkey_patch = functools.partial(monkey_patch, self.function.im_self)
        finally: # function has no attribute im_self (not a method)
            return monkey_patch

    def _handle_decorator(self, decorator_type):
        if isinstance(decorator_type, unicode) or isinstance(decorator_type, str):
            decorator_type = utilities.resolve_string(decorator_type)
        return decorator_type(self.function)

    def _handle_decorators(self, decorator_info):
        decorators = []
        for decorator in decorator_info:
            if isinstance(decorator, str):
                decorator = utilities.resolve_string(decorator)

            decorators.append(decorator)

        wrapped_function = self.function
        for item in reversed(decorators):
            wrapped_function = item(wrapped_function)
        return wrapped_function


class Parser_Metaclass(type):
    """ Provides a command line parser for a class based upon 
        the class.defaults dictionary"""

    parser = argparse.ArgumentParser()
    command_parser = parser.add_subparsers(help="filename")
    run_parser = command_parser.add_parser("run", help="execute the specified script")
    profile_parser = command_parser.add_parser("profile", help="profile the specified script")
    
    def __new__(cls, name, bases, attributes):
        new_class = super(Parser_Metaclass, cls).__new__(cls, name, bases, attributes)
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
        
        new_class = Parser_Metaclass.make_parser(new_class, name, 
                                                 modifiers, exit_on_help)
        return new_class
        
    @staticmethod
    def make_parser(new_class, name, modifiers, exit_on_help):
        parser = Parser_Metaclass.command_parser.add_parser(name)
        new_class.parser = Parser(parser, modifiers, exit_on_help, name)
        return new_class
    
class Parser(object):
    """ Faciltates automatically generated command line parsers. Parser
        instances are class attributes assigned by the Parser_Metaclass"""
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

       
class Instance_Tracker(type):
    """ Provides instance tracking and counting attributes.
    
        Note as of 3/3/2015: the class must implement these attributes,
        it is not performed by this metaclass"""
        
    def __new__(cls, name, bases, attributes):
        if "instance_tracker" not in attributes:
            attributes["instance_tracker"] = {}
        if "instance_count" not in attributes:
            attributes["instance_count"] = 0

        return super(Instance_Tracker, cls).__new__(cls, name, bases, attributes)

       
class Metaclass(Documented, Instance_Tracker, Parser_Metaclass, Method_Hook):
    """ A metaclass that applies other metaclasses. Each metaclass
        in the list Metaclass.metaclasses will be chained into a 
        new single inheritance metaclass that utilizes each entry. 
        The methods insert_metaclass and remove_metaclass may be used
        to alter the contents of this list.
        
        Implementation currently under examination due to compiling with
        cython being broken"""
        
    #metaclasses = [Documented, Instance_Tracker, Parser_Metaclass, Method_Hook]
   # _metaclass = type("Metaclass",
     #                 tuple(metaclasses),
      #                {})
                      
    def __new__(cls, name, bases, attributes):
        # create a new metaclass that uses Metaclass.metaclasses as it's bases.
        #new_metaclass = cls._metaclass
       # print "\nCreating new class: ", name, bases
        new_class = super(Metaclass, cls).__new__(cls, name, bases, attributes)
       # print "New class bases: ", new_class.__bases__
        #print "new class mro: ", new_class.__mro__
        return new_class
    
    @classmethod
    def update_metaclass(cls):
        cls._metaclass = type(cls.__name__,
                              tuple(cls.metaclasses),
                              {})
               
    @classmethod
    def insert_metaclass(cls, metaclass, index=-1):
        cls.metaclasses.insert(index, metaclass)
        cls.update_metaclass()
        
    @classmethod
    def remove_metaclass(cls, metaclass):
        cls.metaclasses.remove(metaclass)
        cls.update_metaclass()
        
        
if __name__ == "__main__":
    import unittest
    import mpre.base as base
    import mpre.defaults      
    
    class Test_Metaclass(unittest.TestCase):
        
        def testdocumentation(self):
            print base.Base.__doc__[:256] + "..."
            print "End documentation test"
            
        def testdecoration(self):
            test_base = base.Base()
            
            def test_decorator1(function):
                def wrapped_function(*args, **kwargs):
                    print "inside local decorator1"
                    return function(*args, **kwargs)
                return wrapped_function
               
            def test_decorator2(function):
                def wrapped_function(*args, **kwargs):
                    print "inside local decorator2"
                    return function(*args, **kwargs)
                return wrapped_function
                
            sock = test_base.create("socket.socket", decorator=test_decorator1)
            
            other_base = test_base.create("mpre.base.Base", decorators=(test_decorator1, test_decorator2))
            
            def monkey_patch(*args, **kwargs):
                print "inside monkey patch"
                
            another_sock = test_base.create("socket.socket", 
                                            monkey_patch=monkey_patch)
            self.failIf(another_sock) # monkey_patch returns False
            
        def testparser(self):
            import sys

            
            backup = sys.argv
            arguments = ("--test_string", "test_value", "--test_int", '8',
                         "--test_bool", "False", "--test_float", 3.14)
            sys.argv = list(arguments)
            print len(sys.argv)

            class TestBase(base.Base):
                defaults = mpre.defaults.Base.copy()
                
                arg_index = 1
                for item in arguments[::2]:
                    defaults[item] = arguments[arg_index]
                    arg_index += 2
                    
            test_base = TestBase(parse_args=True, testattr=1, 
                                 test_string="ishouldn'tbehere")
            
            print "Ensuring parser attribute assignment works"
            
            print "Testing keyword arg assignment..."
            self.failUnless(test_base.testattr == 1)
            
            
            # as above, iteratively for the pairs in sys.argv
            arg_index = 1
            for index, item in enumerate(arguments[::2]):
                value = arguments[arg_index]
                arg_index += 2
                print "Testing {}: {} == {}".format(item, getattr(test_base, item), value)
                self.failUnless(getattr(test_base, item) == value)            
            
            sys.argv = backup
    unittest.main()
'''

base_source = r'''
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
import operator
import inspect
try:
    import cPickle as pickle
except ImportError:
    import pickle
       
import mpre
import mpre.metaclass
import mpre.utilities as utilities
import mpre.defaults as defaults

__all__ = ["DeleteError", "AddError", "Base", "Reactor", "Wrapper", "Proxy"]

DeleteError = type("DeleteError", (ReferenceError, ), {})
AddError = type("AddError", (ReferenceError, ), {})
UpdateError = type("UpdateError", (BaseException, ), {})

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
              of varying verbosity simple and straight forward.
              
            - parallel_method calls. This method is used in a 
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
        
    # the default attributes new instances will initialize with.
    defaults = defaults.Base
    
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

        self.add(instance)
        if not getattr(instance, "_added", False):
            self.environment.add(instance)
        self.environment.Parents[instance] = self.instance_name
        return instance

    def delete(self):
        """usage: object.delete()
            
            Explicitly delete a component. This calls remove and
            attempts to clear out known references to the object so that
            the object can be collected by the python garbage collector"""
        if self.deleted:
            raise DeleteError("{} has already been deleted".format(self.instance_name))
        #print "Beginning deletion of", self.instance_name
        self.environment.delete(self)
        self.deleted = True
        
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
        siblings = objects.get(instance_class, set())
        if instance in siblings:
            raise AddError
        siblings.add(instance)
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
              
    def save(self, attributes=None, _file=None):
        """ usage: base.save([attributes], [_file])
            
            Saves the state of the calling objects __dict__. If _file is not specified,
            a pickled stream is returned. If _file is specified, the stream is written
            to the supplied file like object via pickle.dump.
            
            The attributes argument, if specified, should be a dictionary containing 
            the attribute:value pairs to be pickled instead of the objects __dict__.
            
            If the calling object is one that has been created via the update method, the 
            returned state will include any required source code to rebuild the object."""
            
        self.alert("Saving", level='v')
        # avoid mutating original in case attributes was passed via interpreter session
        attributes = (self.__getstate__() if attributes is None else attributes).copy()
        
        objects = attributes.pop("objects", {})
        saved_objects = attributes["objects"] = {}
        found_objects = []
        for component_type, values in objects.items():
            new_values = []
            for value in sorted(values, key=operator.attrgetter("instance_name")):
                if hasattr(value, "save"):     
                    found_objects.append(value)
                    new_values.append(value.save())
            saved_objects[component_type] = new_values
        
        attribute_type = attributes["_attribute_type"] = {}
        for key, value in attributes.items():
            if value in found_objects:
                attributes[key] = value.instance_name
                attribute_type[key] = "reference"
            elif hasattr(value, "save"):
                attributes[key] = value.save()
                attribute_type[key] = "saved"
           
        if "_required_modules" in attributes: # modules are not pickle-able
            module_info = attributes.pop("_required_modules")
            attributes["_required_modules"] = modules = []
            for name, source, module in module_info[:-1]:
                modules.append((name, source, None))
            modules.append(module_info[-1])
        else:
            attributes["_required_module"] = (self.__module__, self.__class__.__name__)
            
        if _file:
            pickle.dump(attributes, _file)
        else:
            return pickle.dumps(attributes)     
            
    @classmethod
    def load(cls, attributes=None, _file=None):
        """ usage: base_object.load([attributes], [_file]) => restored_instance
        
            Loads state preserved by the save method. The attributes argument, if specified,
            should be a dictionary created by unpickling the bytestream returned by the 
            save method. Alternatively the _file argument may be supplied. _file should be
            a file like object that has previously been supplied to the save method.
            
            Note that unlike save, this method requires either attributes or _file to be
            specified. Also note that if attributes are specified, it should be a dictionary
            that was produced by the save method - simply passing an objects __dict__ will
            result in exceptions.
            
            To customize the behavior of an object after it has been loaded, one should
            extend the on_load method instead of load."""
        assert attributes or _file            
        attributes = attributes.copy() if attributes is not None else pickle.load(_file)
                
        saved_objects = attributes["objects"]
        objects = attributes["objects"] = {}
        for instance_type, saved_instances in saved_objects.items():            
            objects[instance_type] = [cls.load(pickle.loads(instance)) for instance in
                                      saved_instances]

        if "_required_modules" in attributes:
            _required_modules = []
            incomplete_modules = attributes["_required_modules"]
            module_sources = dict((module_name, source) for module_name, source, none in
                                   incomplete_modules[:-1])
            with utilities.modules_switched(module_sources):
                for module_name, source, none in incomplete_modules[:-1]:
                    _required_modules.append((module_name, source, 
                                              utilities.create_module(module_name, source)))
                class_name = incomplete_modules[-1]
                module_name = incomplete_modules[-2][0]
                self_class = getattr(sys.modules[module_name], class_name)
            attributes["_required_modules"] = _required_modules        
        else:
            module_name, class_name = attributes["_required_module"]
            importlib.import_module(module_name)
            self_class = getattr(sys.modules[module_name], class_name)            
        self = self_class.__new__(self_class)
        
        attribute_modifier = attributes.pop("_attribute_type")
        for key, value in attributes.items():
            modifier = attribute_modifier.get(key, '')
            if modifier == "reference":
                attributes[key] = self.environment.Component_Resolve[value]
            elif modifier == "save":
                attributes[key] = cls.load(pickle.loads(value))
                
        self.on_load(attributes)
        self.alert("Loaded", level='v')
        return self
        
    def on_load(self, attributes):
        """ usage: base.on_load(attributes)
        
            Implements the behavior of an object after it has been loaded. This method 
            may be extended by subclasses to customize functionality for instances created
            by the load method."""
        self.set_attributes(**attributes)
        self.environment.add(self)
        if self.instance_name != attributes["instance_name"]:
            self.environment.replace(attributes["instance_name"], self)
                
    def update(self):
        """usage: base_instance.update() => updated_base
        
           Reloads the module that defines base and returns an updated instance. The
           old component is replaced by the updated component in the environment.
           Further references to the object via instance_name will be directed to the
           new, updated object. Attributes of the original object will be assigned
           to the updated object."""
        self.alert("Updating", level='v') 
        # modules are garbage collected if not kept alive        
        required_modules = []        
        class_mro = self.__class__.__mro__[:-1] # don't update object
        class_info = [(cls, cls.__module__) for cls in reversed(class_mro)]
        
        with utilities.modules_preserved(info[1] for info in class_info):
            for cls, module_name in class_info:
                del sys.modules[module_name]
                importlib.import_module(module_name)
                module = sys.modules[module_name]                
                try:
                    source = inspect.getsource(module)
                except TypeError:
                    try:
                        source = module._source
                    except AttributeError:
                        raise UpdateError("Could not locate source for {}".format(module.__name__))
                        
                required_modules.append((module_name, source, module))

        class_base = getattr(module, self.__class__.__name__)
        class_base._required_modules = required_modules
        required_modules.append(self.__class__.__name__)        
        new_self = class_base.__new__(class_base)
                
        # a mini replacement __init__
        attributes = new_self.defaults.copy()
        attributes["_required_modules"] = required_modules
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
        
        This class is a recent addition and is not final in it's api or implementation."""
    
    defaults = defaults.Reactor
    
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
    def __init__(self, **kwargs):
        self.wrapped_object = kwargs.pop("wrapped_object", None)
        super(Wrapper, self).__init__(**kwargs)
                
    def __getattr__(self, attribute):
        return getattr(self.wrapped_object, attribute)        
                       
                       
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
'''

_metapython_source = r'''
import sys
import codeop
import os
import traceback
import time
import cStringIO
import pickle
import contextlib

import mpre
import mpre.base as base
import mpre.vmlibrary as vmlibrary
import mpre.network2 as network2
import mpre.utilities as utilities
import mpre.fileio as fileio
import mpre.defaults as defaults

Instruction = mpre.Instruction            
            
class Shell(network2.Authenticated_Client):
    """ Provides the client side of the interpreter session. Handles keystrokes and
        sends them to the Interpreter_Service to be executed."""
    defaults = defaults.Shell
                     
    def __init__(self, **kwargs):
        super(Shell, self).__init__(**kwargs)
        self.lines = ''
        self.user_is_entering_definition = False            
        self.reaction("User_Input", "add_listener " + self.instance_name)
        
    def login_result(self, sender, packet):
        response = super(Shell, self).login_result(sender, packet)
        if self.logged_in:
            sys.stdout.write(">>> ")
            if self.startup_definitions:
                self.handle_startup_definitions()                
        return response
     
    def handle_startup_definitions(self):
        try:
            compile(self.startup_definitions, "Shell", 'exec')
        except:
            self.alert("Startup defintions failed to compile:\n{}",
                    [traceback.format_exc()],
                    level=0)
        else:
            self.execute_source(self.startup_definitions) 
                    
    def handle_keystrokes(self, sender, keyboard_input):
        if not self.logged_in:
            return
        
        self.lines += keyboard_input
        lines = self.lines
                
        if lines != "\n":            
            try:
                code = codeop.compile_command(lines, "<stdin>", "exec")
            except (SyntaxError, OverflowError, ValueError) as error:
                sys.stdout.write(traceback.format_exc())
                self.prompt = ">>> "
                self.lines = ''
            else:
                if code:
                    if self.user_is_entering_definition:
                        if lines[-2:] == "\n\n":
                            self.prompt = ">>> "
                            self.lines = ''
                            self.execute_source(lines)
                            self.user_is_entering_definition = False              
                    else:
                        self.lines = ''
                        self.execute_source(lines)
                else:
                    self.user_is_entering_definition = True
                    self.prompt = "... "
        else:
            self.lines = ''
        
        sys.stdout.write(self.prompt)
        
    def execute_source(self, source):
        self.reaction(self.target, self.exec_code_request(self.target, source))
        
    def exec_code_request(self, sender, source):
        if not self.logged_in:
            response = self.login(sender, source)
        else:
            self.respond_with("result")
            response = "exec_code " + source
        return response     
        
    def result(self, sender, packet):
        if packet:
            sys.stdout.write("\b"*4 + "   " + "\b"*4 + packet)
        
        
class Interpreter_Service(network2.Authenticated_Service):
    """ Provides the server side of the interactive interpreter. Receives keystrokes
        and attempts to compile + exec them."""
    defaults = defaults.Interpreter_Service
    
    def __init__(self, **kwargs):
        self.user_namespaces = {}
        self.user_session = {}
        super(Interpreter_Service, self).__init__(**kwargs)
        self.log = self.create("fileio.File", "{}.log".format(self.instance_name), 'a+')
                
    def login(self, sender, packet):
        response = super(Interpreter_Service, self).login(sender, packet)
        if "success" in response.lower():
            username = self.logged_in[sender]
            self.user_namespaces[username] = {"__name__" : "__main__",
                                              "__doc__" : '',
                                              "Instruction" : Instruction}
            self.user_session[username] = ''
            string_info = (username, sender,
                           sys.version, sys.platform, self.copyright)
        
            greeting = "Welcome {} from {}\nPython {} on {}\n{}\n".format(*string_info)
            response = "login_result success " + greeting

        return response
        
    @network2.Authenticated
    def exec_code(self, sender, packet):
        log = self.log        
        username = self.logged_in[sender]
        log.write("{} {} from {}:\n".format(time.asctime(), username, sender) + 
                  packet)                  
        result = ''                
        try:
            code = compile(packet, "<stdin>", 'exec')
        except (SyntaxError, OverflowError, ValueError):
            result = traceback.format_exc()           
        else:                
            backup = sys.stdout            
            sys.stdout = cStringIO.StringIO()
            
            namespace = (globals() if username == "root" else 
                         self.user_namespaces[username])
            remove_builtins = False
            if "__builtins__" not in namespace:
                remove_builtins = True
                namespace["__builtins__"] = __builtins__
            try:
                exec code in namespace
            except BaseException as error:
                if type(error) == SystemExit:
                    raise
                else:
                    result = traceback.format_exc()
            else:
                self.user_session[username] += packet
            finally:
                if remove_builtins:
                    del namespace["__builtins__"]
                sys.stdout.seek(0)
                result = sys.stdout.read() + result
                log.write("{}\n".format(result))
                
                sys.stdout.close()
                sys.stdout = backup                
        log.flush()        
        return "result " + result
        
    def __setstate__(self, state):     
        super(Interpreter_Service, self).__setstate__(state)
        sender = dict((value, key) for key, value in self.logged_in.items())
        for username in self.user_session.keys():
            source = self.user_session[username]
            self.user_session[username] = ''
            result = self.exec_code(sender[username], source)
            
        
class Alert_Handler(base.Reactor):
    """ Provides the backend for the base.alert method. This component is automatically
        created by the Metapython component. The print_level and log_level attributes act
        as global filters for alerts; print_level and log_level may be specified as 
        command line arguments upon program startup to globally control verbosity/logging."""
    level_map = {0 : "",
                'v' : "notification ",
                'vv' : "verbose notification ",
                'vvv' : "very verbose notification ",
                'vvvv' : "extremely verbose notification "}
                
    defaults = defaults.Alert_Handler
             
    def __init__(self, **kwargs):
        kwargs["parse_args"] = True
        super(Alert_Handler, self).__init__(**kwargs)
        self.log = self.create("fileio.File", self.log_name, 'a+')
        
    def _alert(self, message, level):
        if not self.print_level or level <= self.print_level:
            sys.stdout.write(message + "\n")
        if level <= self.log_level:
            severity = self.level_map.get(level, str(level))
            # windows will complain about a file in + mode if this isn't done sometimes
            self.log.seek(0, 1)
            self.log.write(severity + message + "\n")
       
            
class Metapython(base.Reactor):
    """ Provides an entry point to the environment. Instantiating this component and
        calling the start_machine method starts the execution of the Processor component.
        It is encouraged to use the Metapython component when create-ing new top level
        components in the environment. For example, the Network component is a child object
        of the Metapython component. Doing so allows for simple portability of an environment
        in regards to saving/loading the state of an entire application."""

    defaults = defaults.Metapython
    parser_ignore = ("environment_setup", "prompt", "copyright", 
                     "traceback", "memory_size", "network_packet_size", 
                     "interface", "port")
    parser_modifiers = {"command" : {"types" : ("positional", ),
                                     "nargs" : '?'},
                        "help" : {"types" : ("short", "long"),
                                  "nargs" : '?'}
                        }
    exit_on_help = False

    def __init__(self, **kwargs):
        super(Metapython, self).__init__(**kwargs)
        self.setup_os_environ()
        self.processor = self.create("vmlibrary.Processor")        
        self.alert_handler = self.create(Alert_Handler)

        if self.startup_definitions:
            Instruction(self.instance_name, "exec_command", 
                        self.startup_definitions).execute() 
                        
        if self.interpreter_enabled:
            Instruction(self.instance_name, "start_service").execute()
     
        with open(self.command, 'r') as module_file:
            source = module_file.read()
        Instruction(self.instance_name, "exec_command", source).execute()
     
    def exec_command(self, source):
        """ Executes the supplied source as the __main__ module"""
        code = compile(source, 'Metapython', 'exec')
        with self.main_as_name():
            exec code in globals(), globals()
            
    @contextlib.contextmanager
    def main_as_name(self):
        backup = globals()["__name__"]        
        globals()["__name__"] = "__main__"
        try:
            yield
        finally:
            globals()["__name__"] = backup
             
    def setup_os_environ(self):
        """ This method is called automatically in Metapython.__init__; os.environ can
            be customized on startup via modifying Metapython.defaults["environment_setup"].
            This can be useful for modifying system path only for the duration of the applications run time."""
        modes = {"=" : "equals",
                 "+=" : "__add__", # append strings or add ints
                 "-=" : "__sub__", # integer values only
                 "*=" : "__mul__",
                 "/=" : "__div__"}

        for command in self.environment_setup:
            variable, mode, value = command.split()
            if modes[mode] == "equals":
                result = value
            else:
                environment_value = os.environ[variable]
                method = modes[mode]
                result = getattr(environment_value, method)(value)
            os.environ[variable] = result
            
    def start_machine(self):
        """ Begins the processing of Instruction objects."""
        self.processor.run()
    
    def start_service(self):
        server_options = {"name" : self.instance_name,
                          "interface" : self.interface,
                          "port" : self.port}        
        self.server = self.create(Interpreter_Service, **server_options)      
        
    def exit(self, exit_code=0):
        self.parallel_method("Processor", "set_attributes", running=False)
        # cleanup/finalizers go here?
        sys.exit(exit_code)
                        
        
class Restored_Interpreter(Metapython):
    """ usage: Restored_Intepreter(filename="suspended_interpreter.bin") => interpreter
    
        Restores an interpreter environment that has been suspended via
        metapython.Metapython.save_state. This is a convenience class
        over Metapython.load_state; note that instances produced by instantiating
        Restored_Interpreter will be of the type of instance returned by
        Metapython.load_state and not Restored_Interpreter"""
        
    defaults = defaults.Metapython.copy()
    defaults.update({"filename" : 'Metapython.state'})
    
    def __new__(cls, *args, **kwargs):
        instance = super(Restored_Interpreter, cls).__new__(cls, *args, **kwargs)
        attributes = cls.defaults.copy()
        if kwargs.get("parse_args"):
            attributes.update(instance.parser.get_options(cls.defaults))       
        
        with open(attributes["filename"], 'rb') as save_file:
            interpreter = pickle.load(save_file)
        
        return interpreter
'''

network_source = r'''
#   mpf.network_library - Asynchronous socket operations
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
import socket
import select
import struct
import errno
import traceback

import mpre
import mpre.vmlibrary as vmlibrary
import mpre.defaults as defaults
import mpre.base as base
from utilities import Latency, Average
Instruction = mpre.Instruction

NotWritableError = type("NotWritableError", (IOError, ), {"errno" : -1})
ERROR_CODES = {-1 : "NotWritableError"}
try:
    CALL_WOULD_BLOCK = errno.WSAEWOULDBLOCK
    BAD_TARGET = errno.WSAEINVAL
    CONNECTION_IN_PROGRESS = errno.WSAEWOULDBLOCK
    CONNECTION_IS_CONNECTED = errno.WSAEISCONN
    CONNECTION_WAS_ABORTED = errno.WSAECONNABORTED
    CONNECTION_RESET = errno.WSAECONNRESET    
    ERROR_CODES[BAD_TARGET] = "BAD_TARGET"    
except:
    CALL_WOULD_BLOCK = errno.EWOULDBLOCK
    CONNECTION_IN_PROGRESS = errno.EINPROGRESS
    CONNECTION_IS_CONNECTED = errno.EISCONN
    CONNECTION_WAS_ABORTED = errno.ECONNABORTED
    CONNECTION_RESET = errno.ECONNRESET
 
ERROR_CODES.update({CALL_WOULD_BLOCK : "CALL_WOULD_BLOCK",
                    CONNECTION_IN_PROGRESS : "CONNECTION_IN_PROGRESS",
                    CONNECTION_IS_CONNECTED : "CONNECTION_IS_CONNECTED",
                    CONNECTION_WAS_ABORTED : "CONNECTION_WAS_ABORTED",
                    CONNECTION_RESET  : "CONNECTION_RESET"})
               
HOST = socket.gethostbyname(socket.gethostname())

class Error_Handler(object):
            
    def connection_reset(self, sock, error):
        sock.alert("Connection reset\n{}", [error], level=0)
        sock.delete()
        
    def connection_was_aborted(self, sock, error):
        sock.alert("Connection was aborted\n{}", [error], level=0)
        sock.delete()
        
    def eagain(self, sock, error):
        sock.alert("{}", [error], level=0)
    
    def bad_target(self, sock, error):
        sock.alert("Invalid target {}; {} {}", 
                   [getattr(sock, "target", ''), errno.errorcode[error.errno], error], 
                   level=0)
        sock.delete()
        
    def unhandled(self, sock, error):
        sock.alert("Unhandled error:{} {}", [errno.errorcode[error.errno], error], level=0)
        sock.delete()
        
_error_handler = Error_Handler()
       
class Socket(base.Wrapper):
    """ Provides a mostly transparent asynchronous socket interface by applying a 
        Wrapper to a _socketobject. The default socket family is socket.AF_INET and
        the default socket type is socket.SOCK_STREAM (a.k.a. a tcp socket)."""
    defaults = defaults.Socket

    def _get_address(self):
        return (self.ip, self.port)
    address = property(_get_address)
    
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM,
                       proto=0, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(family, type, proto))
        self.error_handler = _error_handler
        super(Socket, self).__init__(**kwargs)
        self.socket = self.wrapped_object
        self.setblocking(self.blocking)
        self.settimeout(self.timeout)
                
        if self.add_on_init:
            self.added_to_network = True
            self.parallel_method("Network", "add", self)
         
    def on_select(self):
        """ Used to customize behavior when a socket is readable according to select.select.
            It is not likely that one would overload this method; End users probably want
            to overload recv/recvfrom instead."""
        self.recvfrom(self.network_packet_size)
        
    def send(self, data):
        """ Sends data via the underlying _socketobject. The socket is first checked to
            ensure writability before sending. If the socket is not writable, NotWritableError is raised. Usage of this method requires a connected socket"""
        if self.parallel_method("Network", "is_writable", self):
            return self.wrapped_object.send(data)
        else:
            raise NotWritableError
                             
    def sendto(self, data, host_info):
        """ Sends data via the underlying _socketobject to the specified address. The socket
            is first checked to ensure writability before sending. If the socket is not
            writable, NotWritableError is raised."""
        if self.parallel_method("Network", "is_writable", self):
            return self.wrapped_object.sendto(data, host_info)
        else:
            raise NotWritableError

    def recv(self, buffer_size=0):
        """ Receives data from a remote endpoint. This method is event triggered and called
            when the socket becomes readable according to select.select. Subclasses should
            extend this method to customize functionality for when data is received. This
            method is called for Tcp sockets and requires a connection."""
        buffer_size = (self.network_packet_size if not buffer_size else
                       buffer_size)
        return self.wrapped_object.recv(buffer_size)
        
    def recvfrom(self, buffer_size=0):
        """ Receives data from a host. For Udp sockets this method is event triggered
            and called when the socket becomes readable according to select.select. Subclasses
            should extend this method to customize functionality for when data is received."""
        buffer_size = (self.network_packet_size if not buffer_size else
                       buffer_size)
        return self.wrapped_object.recvfrom(buffer_size)
      
    def connect(self, address):
        """ Perform a non blocking connect to the specified address. The on_connect method
            is called when the connection succeeds, or the appropriate error handler method
            is called if the connection fails. Subclasses should overload on_connect instead
            of this method."""
        print address
        try:
            self.wrapped_object.connect(address)
        except socket.error as error:
            if error.errno != 10035:
                raise
            if not self._connecting:
                self._connecting = True
                self.parallel_method("Network", "connect", self)            

    def on_connect(self):
        """ Performs any logic required when a Tcp connection succeeds. This method should
            be overloaded by subclasses."""
        self.alert("Connected", level=0)
                
    def delete(self):
        if not self.closed:
            self.close()            
        super(Socket, self).delete()
    
    def close(self):
        if self.added_to_network:
            self.parallel_method("Network", "remove", self)
        self.wrapped_object.close()
        self.closed = True
    
    def __getstate__(self):
        stats = super(Socket, self).__getstate__()
        del stats["wrapped_object"]
        del stats["socket"]
        return stats
        
       
class Tcp_Socket(Socket):

    defaults = defaults.Tcp_Socket
    
    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET,
                                                          socket.SOCK_STREAM))
        super(Tcp_Socket, self).__init__(**kwargs)

    def on_select(self):
        self.recv(self.network_packet_size)
        
        
class Server(Tcp_Socket):

    defaults = defaults.Server

    def __init__(self, **kwargs):       
        super(Server, self).__init__(**kwargs)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, self.reuse_port)

        bind_success = True
        try:
            self.bind((self.interface, self.port))
        except socket.error:
            self.alert("socket.error when binding to {0}", (self.port, ), 0)
            bind_success = self.handle_bind_error()
        if bind_success:
            self.listen(self.backlog)
                    
    def on_select(self):
        try:
            while True:
                self.accept()
        except socket.error as error:
            if error.errno != 10035:
                raise
                
    def accept(self):
        _socket, address = self.wrapped_object.accept()
        
        connection = self.create(self.Tcp_Socket_type,
                                 wrapped_object=_socket)
        
        self.alert("{} accepted connection {} from {}", 
                  (self.name, connection.instance_name, address),
                  level="v")
        
        self.on_connect(connection)
        return connection, address
        
    def handle_bind_error(self):
        if self.allow_port_zero:
            self.bind((self.interface, 0))
            return True
        else:
            self.alert("{0}\nAddress already in use. Deleting {1}\n",
                       (traceback.format_exc(), self.instance_name), 0)
            instruction = Instruction(self.instance_name, "delete")
            instruction.execute()
 
    def on_connect(self, connection):
        """ Connection logic that the server should apply when a new client has connected.
            This method should be overloaded by subclasses"""
        raise NotImplementedError 
        
        
class Tcp_Client(Tcp_Socket):

    defaults = defaults.Tcp_Client

    def __init__(self, **kwargs):
        super(Tcp_Client, self).__init__(**kwargs)
        
        if not self.target:
            if not self.ip:
                self.alert("Attempted to create Tcp_Client with no host ip or target", tuple(), 0)
            self.target = (self.ip, self.port)
        if self.auto_connect:
            self.connect(self.target)
                
        
class Udp_Socket(Socket):

    defaults = defaults.Udp_Socket

    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        super(Udp_Socket, self).__init__(**kwargs)        
               
        if self.bind_on_init:
            self.bind((self.interface, self.port))
            
        if not self.port:
            self.port = self.getsockname()[1]
        
        
class Multicast_Beacon(Udp_Socket):

    defaults = defaults.Multicast_Beacon

    def __init__(self, **kwargs):
        super(Multicast_Beacon, self).__init__(**kwargs)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.packet_ttl)


class Multicast_Receiver(Udp_Socket):

    defaults = defaults.Multicast_Receiver

    def __init__(self, **kwargs):
        super(Multicast_Receiver, self).__init__(**kwargs)

        # thanks to http://pymotw.com/2/socket/multicast.html for the below
        group_option = socket.inet_aton(self.address)
        multicast_configuration = struct.pack("4sL", group_option, socket.INADDR_ANY)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_configuration)
           

class Network(vmlibrary.Process):
    """ Manages socket objects and is responsible for calling select.select to determine
        readability/writability of sockets. Also responsible for non blocking connect logic. 
        This component is created by default upon application startup, and in most cases will
        not require user interaction."""
    defaults = defaults.Network
   
    def __init__(self, **kwargs):
        # minor optimization; pre allocated slices and ranges for
        # sliding through the socket list to sidestep the 500 
        # file descriptor limit that select has. Produces slice objects
        # for ranges 0-500, 500-1000, 1000-1500, etc, up to 50000.
        self._slice_mapping = dict((x, slice(x * 500, (500 + x * 500))) for 
                                    x in xrange(100))
        self._socket_range_size = range(1)
        
        self._writable = set()
        self.connecting = set()
        super(Network, self).__init__(**kwargs)
        
        self.sockets = []
        self._sockets = set()
        self.running = False
        self.update_instruction = Instruction(self.instance_name, "_update_range_size")
        self.update_instruction.execute(self.update_priority)
        
    def add(self, sock):
        super(Network, self).add(sock)
        self.sockets.append(sock)
        self._sockets.add(sock)
        if not self.running:
            self.running = True        
            self.run()
                
    def remove(self, sock):
        super(Network, self).remove(sock)
        self.sockets.remove(sock)
        self._sockets.remove(sock)
        if sock in self.connecting:
            self.connecting.remove(sock)
            
    def delete(self):
        super(Network, self).delete()
        del self.sockets
        del self._sockets
        
    def _update_range_size(self):
        load = self._socket_range_size = range((len(self.sockets) / 500) + 1)
        # disable sleep under load
        self.priority = self.defaults["priority"] if len(load) == 1 else 0.0 
        self.update_instruction.execute(self.update_priority)

    def run(self):
        sockets = self.sockets
        if not sockets:
            self.running = False
        else:
            for chunk in self._socket_range_size:
                # select has a max # of file descriptors it can handle, which
                # is about 500 (at least on windows). We can avoid this limitation
                # by sliding through the socket list in slices of 500 at a time
                socket_list = sockets[self._slice_mapping[chunk]]
                readable, writable, errors = select.select(socket_list, socket_list, [], 0.0)
                                
                writable = self._writable = set(writable)
                connecting = self.connecting
                
                if connecting:
                    # if a tcp client is writable, it's connected
                    accepted_connections = connecting.intersection(writable)
                    if accepted_connections:
                        for accepted in connecting.intersection(writable):
                            accepted.on_connect()
                        
                    # if not, then it's still connecting or the connection failed
                    still_connecting = connecting.difference(writable)    
                    expired = set()                    
                    if still_connecting:                        
                        for connection in still_connecting:
                            connection.connection_attempts -= 1
                            if not connection.connection_attempts:
                                try:
                                    connection.connect(connection.target)
                                except socket.error as error:
                                    expired.add(connection)
                                    handler = getattr(connection.error_handler, 
                                        ERROR_CODES[error.errno].lower(),
                                        connection.error_handler.unhandled)
                                    handler(connection, error)                                   
                    self.connecting = still_connecting.difference(expired)       
                if readable:
                    for sock in readable:
                        try:
                            sock.on_select()
                        except socket.error as error:
                            handler = getattr(sock.error_handler, 
                                    ERROR_CODES[error.errno].lower(),
                                    sock.error_handler.unhandled)
                            handler(sock, error)         
            self.run_instruction.execute(priority=self.priority)
                   
    def connect(self, sock):
        self.connecting.add(sock)
                
    def is_writable(self, sock):
        return sock in self._writable
'''

shell_launcher_source = r'''
import mpre

Instruction = mpre.Instruction

options = {"parse_args" : True,
           "startup_definitions" : ''}

# feel free to customize
definitions = \
"""import base

constructor = base.Base()
environment = constructor.environment
    
create = constructor.create

def print_components(mode="keys", size=(None, )):
    _slice = slice(*size)
    print getattr(constructor.environment.Component_Resolve, mode)()[_slice]

def get_component(instance_name):
    return constructor.environment.Component_Resolve[instance_name]

def delete(instance_name):
    constructor.parallel_method(instance_name, "delete")
                    
def build_docs(**kwargs):    
    return constructor.parallel_method("Metapython", "create", 
                                       "mpre.package.Documentation", **kwargs)
                 
def update(component):
    return constructor.parallel_method(component, "update")
    
#proxy = constructor.create("network2.Tcp_Service_Proxy", port=39999)
#import network2
#rpc = network2.Remote_Procedure_Call("Interpreter_Service", "login", ("127.0.0.1", 39999), 
#                                     "root2 password")
#connection = rpc.execute()                        
"""

options["startup_definitions"] += definitions

if __name__ == "__main__":
    Instruction("Metapython", "create", "metapython.Shell", **options).execute()
'''

def create_module(module_name, source, attach_source=False):
    """ Creates a module with the supplied name and source"""
    module_code = compile(source, module_name, 'exec')
    new_module = types.ModuleType(module_name)
    exec module_code in new_module.__dict__
    if attach_source:
        assert not hasattr(new_module, "_source")
        new_module._source = source
    return new_module


class Importer(object):
    
    def __init__(self):
        super(Importer, self).__init__()
        
    def find_module(self, module_name, path):        
        if module_name[:4] == "mpre":
            _module_name = module_name.split(".", 1)[-1]
            if "{}_source".format(_module_name) in globals():
                return self
        return None
        
    def load_module(self, module_name):        
        if module_name in sys.modules:
            return sys.modules[module_name]
        _module_name = module_name.split(".", -1)[-1]        
        module = create_module(module_name, globals()["{}_source".format(_module_name)],
                               attach_source=True)
        sys.modules[module_name] = module
        return module        


sys.meta_path = [Importer()]

if __name__ == '__main__':
    import mpre._metapython
    metapython = mpre._metapython.Metapython(parse_args=True)
    metapython.start_machine()