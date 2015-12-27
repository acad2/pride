""" Additional builtin functions that are generally, frequently, and obviously useful.
    Functions defined here become available as builtins when pride is imported.
    Default builtins can be replaced by defining them here
    
    This module should only receive additions when absolutely necessary. """    
import sys
import importlib
import platform
is_version_two = platform.python_version_tuple()[0] == '2'

__all__ = ("slide", "resolve_string", "raw_input" if is_version_two else "input")

# too generally applicable to have to import, only vaguely appropriate other module is utilities
def slide(iterable, x=16):
    """ Yields x bytes at a time from iterable """
    slice_count, remainder = divmod(len(iterable), x)
    for position in range((slice_count + 1 if remainder else slice_count)):
        yield iterable[position * x:x * (position + 1)]  
        
# used in way too many places. no need to bother importing utilities everywhere       
def resolve_string(module_name):
    """Given an attribute string of a.b...z, return the object z"""
    result = None
    _original = module_name
    attributes = []
    while not result:
        try:
            result = (sys.modules[module_name] if module_name in 
                      sys.modules else importlib.import_module(module_name))
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
    
if is_version_two:    
    __raw_input = raw_input
    
    def raw_input(prompt='', must_reply=False):
        """ raw_input function that plays nicely when sys.stdout is swapped.
            If must_reply equals True, then the prompt will be redisplayed
            until a non empty string is returned.
            
            For documentation of the standard CPython raw_input function, consult
            the python interpreter or the internet. """
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
    