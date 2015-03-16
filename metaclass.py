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
        Documented.make_docstring(attributes)
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
            
    def _handle_context_manager(self, context_manager):
        raise NotImplementedError
        if isinstance(context_manager, str):
            context_manager = utilities.resolve_string(context_manager)
        return context_manager   

        with context_manager():
            result = self.function(*args, **kwargs)
        return result

    def _handle_monkey_patch(self, monkey_patch):
        if isinstance(monkey_patch, str):
            monkey_patch = utilities.resolve_string(patch_info)
        try:
            monkey_patch = functools.partial(monkey_patch, self.function.im_self)
        finally: # function has no attribute im_self (not a method)
            return monkey_patch

    def _handle_decorator(self, decorator_type):
        if isinstance(decorator_type, str):
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

        
class Metaclass(Documented):
    """ A metaclass that applies other metaclasses. Each metaclass
        in the list Metaclass.metaclasses will be chained into a 
        new single inheritance metaclass that utilizes each entry. 
        The methods insert_metaclass and remove_metaclass may be used
        to alter the contents of this list."""
        
    metaclasses = [Instance_Tracker, Parser_Metaclass, Method_Hook]
    
    def __new__(cls, name, bases, attributes):
        new_metaclass = type(Metaclass.__name__,
                             tuple(Metaclass.metaclasses),
                             {})
        new_class = new_metaclass.__new__(new_metaclass, name, bases, attributes)
        return new_class
        
    @classmethod
    def insert_metaclass(metaclass, index=-1):
        Metaclass.metaclasses.insert(index, metaclass)
    
    @classmethod
    def remove_metaclass(metaclass):
        Metaclass.metaclasses.remove(metaclass)

        
if __name__ == "__main__":
    import unittest
    import mpre.base
    import mpre.defaults      
    
    class Test_Metaclass(unittest.TestCase):
        
        def testdocumentation(self):
            print mpre.base.Base.__doc__[:256] + "..."
            print "End documentation test"
            
        def testdecoration(self):
            test_base = mpre.base.Base()
            
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

            class TestBase(mpre.base.Base):
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