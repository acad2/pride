""" Additional builtin functions that are generally, frequently, and obviously useful.
    Functions defined here become available as builtins when pride is imported.
    Default builtins can be replaced by defining them here
    
    This module should only receive additions when absolutely necessary. """    
import sys
import importlib
import platform
import itertools
import pprint
is_version_two = platform.python_version_tuple()[0] == '2'

__all__ = ("slide", "resolve_string", "raw_input" if is_version_two else "input", 
           "restart", "shutdown", "objects", "invoke", "system_update")

_NUMBERS = ''.join(str(x) for x in xrange(10))

# too generally applicable to have to import, only vaguely appropriate other module is utilities
def slide(iterable, x=1):
    """ Yields x bytes at a time from iterable """
    slice_count, remainder = divmod(len(iterable), x)
    for position in range((slice_count + 1 if remainder else slice_count)):
        _position = position * x
        yield iterable[_position:_position + x]        
        
# used in way too many places. no need to bother importing utilities everywhere       
def resolve_string(module_name):
    """Given an attribute string of a.b...z, return the object z, importing 
       any required packages and modules to access z.
       
       Alternatively, resolves a reference from the objects dictionary, and 
       potentially loads a specified attribute i.e.:
        
        resolve_string("->Python") == objects["->Python"]
        resolve_string("->User->Shell.logged_in") == objects["->User->Shell"].logged_in"""
    if module_name[:2] == "->":
        try:
            reference, attribute = module_name.split('.', 1)
        except ValueError:
            result = objects[module_name]
        else:
            result = getattr(objects[reference], attribute)
    elif module_name in __builtins__:
        result = __builtins__[module_name]
    else:        
        result = None
        _original = module_name
        attributes = []
        modules = sys.modules
        import_module = importlib.import_module
        while not result:
            try:
                result = (modules[module_name] if module_name in 
                          modules else import_module(module_name))
            except ImportError:
                module_name = module_name.split('.')
                attributes.append(module_name.pop())
                module_name = '.'.join(module_name)
            except ValueError:
                raise ValueError("Unable to load package or module: {}".format(_original))
        try:
            for attribute in reversed(attributes):
                result = getattr(result, attribute)
        except AttributeError:
            error_message = "unable to load {} from {}; failed to resolve string '{}'"
            print error_message.format(attribute, result, _original)
            raise
    return result        
    
def invoke(callable_string, *args, **kwargs):
    """ Calls the method named in callable_string with args and kwargs.
     
        Base objects that are created via invoke instead of create will
        exist as a root object in the objects dictionary. """
    return resolve_string(callable_string)(*args, **kwargs)
        
if is_version_two:    
    __raw_input = raw_input
    class RequestDenied(BaseException): pass
    
    def raw_input(prompt='', must_reply=False):
        """ raw_input function that plays nicely when sys.stdout is swapped.
            If must_reply equals True, then the prompt will be redisplayed
            until a non empty string is returned.
            
            For documentation of the standard CPython raw_input function, consult
            the python interpreter or the internet. """        
        if getattr(objects.get("->Python->Interpreter", None), "_disable_raw_input", None):
            raise RequestDenied("raw_input does not function remotely and would block")        
        if must_reply:
            reply = ''
            while not reply:
                sys.__stdout__.write(prompt)
                sys.__stdout__.flush()
                reply = __raw_input('')
        else:
            sys.__stdout__.write(prompt)
            sys.__stdout__.flush()
            reply = __raw_input('')
        return reply    
else:
    __input = input
    def input(prompt='', must_reply=False):
        """ input function that plays nicely when sys.stdout is swapped.
            If must_reply equals True, then the prompt will be redisplayed
            until a non empty string is returned.
            
            For documentation of the standard CPython input function, consult
            the python interpreter or the internet. """
        if must_reply:
            reply = ''
            while not reply:
                sys.__stdout__.write(prompt)
                sys.__stdout__.flush()        
                reply = __input('')
        else:
            sys.__stdout__.write(prompt)
            sys.__stdout__.flush()       
            reply = __input('')
        return reply    
    
def restart():
    raise SystemExit("Restart")
    
def system_update():
    for reference, root_object in ((reference, _object) for reference, _object in 
                                    objects.items() if reference.count("->") == 1):      
        if reference not in ("->Finalizer", "->Alert_Handler"):            
            root_object.update(True)
    
def shutdown():
    raise SystemExit(0)
               
objects = {}#Objects_Dictionary()
