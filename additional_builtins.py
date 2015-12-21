""" Additional builtin functions that are generally and frequently useful.
    Functions defined here become available as builtins when pride is imported. """    
import sys
import importlib

__all__ = ("slide", "resolve_string")

def slide(iterable, x=16):
    """ Yields x bytes at a time from iterable """
    slice_count, remainder = divmod(len(iterable), x)
    for position in range((slice_count + 1 if remainder else slice_count)):
        yield iterable[position * x:x * (position + 1)]  
        
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