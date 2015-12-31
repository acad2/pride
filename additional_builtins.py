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
           "restart", "shutdown", "objects", "_root_objects")

_root_objects = {}

_NUMBERS = ''.join(str(x) for x in xrange(10))

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
    
def restart():
    raise SystemExit(-1)
    
def shutdown():
    raise SystemExit(0)
       
def _relative_name_lookup(value):    
    if value.count("->") == 1:
        return _root_objects[value]
    else:
        root_name, children = value[2:].split("->", 1)            
        current_object = _root_objects["->" + root_name]
        for child_name in children.split("->"):
       #     print "Resolving child: ", child_name
            for number_count, character in enumerate(reversed(child_name)):
                if character not in _NUMBERS:
                    break
            index = int(child_name[-number_count:]) if number_count else 0
         #   print "Parent: ", current_object
         #   print "Parent objects: ", current_object.objects
            current_object = (current_object.objects[child_name[:-number_count or None]]
                                                    [index])
        return current_object
            
class Objects_Dictionary(object):    
            
    def __getitem__(self, value):         
        if "->" not in value:
            raise KeyError("{}".format(value))        
        try:
            return _relative_name_lookup(value)
        except IndexError:
            raise KeyError("'{}' not in objects".format(value))
    
    #def __setitem__(self, item, value):
    #    current_object = self[item]
    #    parent_objects = current_object.parent.objects
    #    index = parent_objects.index(current_object)
    #    parent_object.insert(index, value)
    #    del parent_objects[index + 1]
        
   # def __delitem__(self, item):
    #    current_object = self[item]
        
        
    def _recursive_search(self, __object, retrieve="keys", result=None):
        result = result or []
        for _object in itertools.chain(*__object.objects.values()):
            if retrieve == "keys":
                result.append(_object.reference)
                self._recursive_search(_object, "keys", result)
            elif retrieve == "values":
                result.append(_object)
                self._recursive_search(_object, "values", result)
            elif retrieve == "items":
                result.append((_object.reference, _object))
                self._recursive_search(_object, "items", result)
            else:
                raise ValueError("Unsupported retrieve flag '{}'".format(retrieve))            
        return result
            
    def keys(self):
        keys = []
        for root_name, root_object in _root_objects.items():
            keys.append(root_name)           
            self._recursive_search(root_object, "keys", keys)
        return keys
            
    def values(self):
        values = []
        for root_name, root_object in _root_objects.items():
            values.append(root_object)
            self._recursive_search(root_object, "values", values)
        return values
        
    def items(self):
        items = []
        for item in _root_objects.items():
            items.append(item)
            self._recursive_search(item[1], "items", items)
        return items        
    
    def __len__(self):
        return len(self.keys())
   
    def get_dict(self):
        return dict((key, value) for key, value in self.items())
            
    def __str__(self):
        return str(self.get_dict())
                
    def __contains__(self, value):
        return value in self.keys()
        
objects = {}#Objects_Dictionary()
