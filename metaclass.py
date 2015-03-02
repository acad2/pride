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
    """ Faciltates automatically generated command line parsers. Parser
        instances are class attributes assigned by the Metaclass"""
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
    """ The metaclass for mpre.base.Base. This metaclass is responsible for
        applying instance tracking information to the class, a parser for
        the class, and wrapping the class methods in Runtime_Decorators."""
    
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