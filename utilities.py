import shlex
import sys
import time
import inspect
import subprocess
import collections
import contextlib
import importlib
import types
import pprint
import traceback
import timeit

from persistence import save_data, load_data
timestamp = timeit.default_timer    
     
_TYPE_SYMBOL = {int : chr(0), float : chr(1), str : chr(2), 
                bool : chr(3), list : chr(4), dict : chr(5),
                tuple : chr(6), set : chr(7), type(None) : chr(8),
                unicode : chr(9), BaseException : chr(10), long : chr(11)}
                
_TYPE_RESOLVER = {_TYPE_SYMBOL[int] : int, _TYPE_SYMBOL[bool] : lambda value: True if value == "True" else False,
                  _TYPE_SYMBOL[float] : float, _TYPE_SYMBOL[type(None)] : lambda value: None,                                   
                  _TYPE_SYMBOL[str] : lambda value: value,
                  _TYPE_SYMBOL[unicode] : unicode, _TYPE_SYMBOL[long] : long}                         
                
def isancestor(ancestor, descendant):
    """ usage: isancestor(ancestor, descendant) => (True or False)
    
        Returns True if ancestor is an ancestor of descendant (i.e. a parent, grandparent, great grandparent, etc).
        Returns False is ancestor is not an ancestor of descendant.
        
        Note that this method only works with Base objects. """
    while descendant and descendant.parent != ancestor:
        descendant = descendant.parent
    return bool(descendant.parent if descendant is not None else descendant)
    
def isdescendant(descendant, ancestor):
    """ usage: isdescendant(descendant, ancestor)
        
        Returns True if ancestor is an ancestor of descendant (i.e. a parent, grandparent, great grandparent, etc).
        Returns False is ancestor is not an ancestor of descendant.
        
        Note that this method only works with Base objects. """
    return isancestor(ancestor, descendant)
                
def splice(new_bytes, into='', at=0):
    return into[:at] + new_bytes + into[at + len(new_bytes):]
    
def rotate(input_string, amount):
    """ Rotate input_string by amount. Amount may be positive or negative.
        Example:
            
            >>> data = "0001"
            >>> rotated = rotate(data, -1) # shift left one
            >>> print rotated
            >>> 0010
            >>> print rotate(rotated, 1) # shift right one, back to original
            >>> 0001 """
    if not amount or not input_string:            
        return input_string    
    else:
        amount = amount % len(input_string)
        return input_string[-amount:] + input_string[:-amount]
                                                        
def print_in_place(_string):
    sys.stdout.write(_string + '\r')
    sys.stdout.flush()
                                  
def updated_class(_class):
    # modules are garbage collected if not kept alive            
    import module_utilities
    required_modules = module_utilities.get_all_modules_for_class(_class)    
    class_base = getattr(required_modules[-1][2], _class.__name__)
    class_base._required_modules = required_modules
    return class_base
    
def convert(old_value, old_base, new_base):
    """ Converts a number in an arbitrary base to the equivalent number
        in another. 
        
        old_value is a string representation of the number to be converted,
        represented in old_base.
        
        new_base is the symbol set to be converted to.
        
        old_base and new_base are iterables, most commonly string or list. """
    old_base_size = len(old_base)    
    old_base_mapping = dict((symbol, index) for index, symbol in enumerate(old_base))
            
    for leading_zero_count, symbol in enumerate(old_value):
        if old_base_mapping[symbol]:
            break
    zero_padding = new_base[0] * leading_zero_count
    
    decimal_value = sum((old_base_mapping[value_representation] * (old_base_size ** power) for
                         power, value_representation in enumerate(reversed(old_value))))
    
    # this is the above in a potentially more readable format:
    # decimal_value = 0    
    # for power, value_representation in enumerate(reversed(old_value)):
    #     decimal_value += old_base_mapping[value_representation]*(old_base_size**power)
                            
    if decimal_value:
        new_base_size = len(new_base)    
        new_value = ''
        while decimal_value > 0: # divmod = divide and modulo in one action
            decimal_value, digit = divmod(decimal_value, new_base_size)
            new_value += new_base[digit]
    return zero_padding + ''.join(reversed(new_value))  
    
def shell(command, shell=False):
    """ usage: shell('command string --with args', 
                     [shell=False]) = > sys.stdout.output from executed command
                    
        Launches a process on the physical machine via the operating 
        system shell. The shell and available commands are OS dependent.
        
        Regarding the shell argument; from the python docs on subprocess.Popen:
            "The shell argument (which defaults to False) specifies whether to use the shell as the program to execute. If shell is True, it is recommended to pass args as a string rather than as a sequence."
            
        and also:        
            "Executing shell commands that incorporate unsanitized input from an untrusted source makes a program vulnerable to shell injection, a serious security flaw which can result in arbitrary command execution. For this reason, the use of shell=True is strongly discouraged in cases where the command string is constructed from external input" """        
    if not shell:
        command = shlex.split(command)        
    process = subprocess.Popen(command, shell=shell)
    return process.communicate()[0]
    
def function_header(function):
    """usage: function_header(function) => "(arg1, default_arg=True, keyword=True...)"
    
       Given a function, return a string of it's signature."""
    try:
        code = function.func_code
    except AttributeError:
        try:
            code = function.im_func.func_code
        except AttributeError:
            try:
                code = function.im_func.func.func_code
            except AttributeError:
                raise ValueError("could not locate code object of {}".format(function))
        
    arguments = inspect.getargs(code)
    _arguments = ', '.join(arguments.args)
    if arguments.varargs:
        prefix = ", *" if _arguments else ''
        _arguments += prefix + arguments.varargs
    if arguments.keywords:
        prefix = ", **"  if _arguments else ''
        _arguments += prefix + arguments.keywords
    return "(" + _arguments + ")"    
      
def usage(_object):
    if hasattr(_object, "func_name"):
        name = _object.func_name
        arguments = function_header(_object)
        return_type = ''#pride.misc.bytecodedis.get_return_type(_object)
    elif hasattr(_object, "func_code"):
        name = _object.__name__
        arguments = function_header(_object)
        return_type = ''
    elif hasattr(_object, "function"):
        name = _object.__name__
        arguments = function_header(_object.function)
        return_type = ''
    elif hasattr(_object, "defaults") and isinstance(_object.defaults, dict):
        name = _object.__name__ if isinstance(_object, type) else type(_object).__name__
        spacing = ''
        arguments = '({'
        for attribute, value in _object.defaults.items():
            arguments += spacing + attribute + " : " + str(value)
            spacing = '\n' + (len(name) + len("usage: ({")) * " "
        arguments += "})"    
        return_type = " => {}".format(name)
    elif type(_object).__name__ == "Runtime_Decorator":
        name = _object.function.__name__
        arguments = function_header(_object.function)
        return_type = ''
    elif hasattr(_object, "__call__"):
        name = _object.__name__ if isinstance(_object, type) else type(_object).__name__
        arguments = function_header(_object)
        return_type = ''
    else:
        raise ValueError("Unsupported object: {}".format(_object))
    return "usage: {}{}{}".format(name, arguments, return_type)
    
def documentation(_object):
    new_section = "{}\n==============\n\n"
    new_subsection = "\n\n{}\n--------------\n\n"
    if isinstance(_object, types.ModuleType):        
        module_name = _object.__name__
        docstring = new_section.format(module_name)
        docstring += _object.__doc__ if _object.__doc__ is not None else ''
        
        for attribute in (attribute for attribute in dir(_object) if "_" != attribute[0]):
            value = getattr(_object, attribute)
            if isinstance(value, type) or callable(value) and "built-in" not in str(value):
                docs = documentation(value)
                if docs:
                    docstring += new_subsection.format(attribute) + docs #"\n\n" + docs#
            
    elif isinstance(_object, type):
        class_name = _object.__name__
        docstring = ''#new_subsection.format(class_name)
        docs = _object.__dict__["__doc__"]
        if docs.__class__.__name__ == "Docstring":
            docs = _object.__doc    
        elif docs is None:
            docs = "No documentation available"
        docstring += '\t' + docs + "\n" #docs.replace("\n", "\n\t\t") + "\n"
        
        if hasattr(_object, 'defaults'):
            docstring += '\n\n' + "Instance defaults: \n\n\t"
            docstring += pprint.pformat(_object.defaults).replace("\n", "\n\t")
           
        docstring += "\n\n" + "Method resolution order: \n\n\t" + pprint.pformat(_object.__mro__).replace("\n", "\n\t")
        
        for attribute in (attribute for attribute in 
                          _object.__dict__.keys() if "_" != attribute[0]):
            value = getattr(_object, attribute)
            if "Runtime_Decorator" == value.__class__.__name__:
                docs = documentation(value.function)
                docstring += "\n\n" + docs
            elif callable(value):#hasattr(value, "im_func"):
                docs = documentation(value)           
                docstring += "\n\n- " + docs
                
    elif callable(_object):
        try:
            function_name = _object.__name__
        except AttributeError:
            docstring = ''
        else:
            new_function = "**{}**"
            beginning = "usage: " + function_name            
            try:
                docstring = (new_function.format(function_name) + 
                             usage(_object)[len(beginning):] + ":")
            except ValueError:
                docstring = new_function.format(function_name) + ":"
            docstring += "\n\n\t\t"
            docstring += (_object.__doc__ if _object.__doc__ is not None else 
                          "\t\tNo documentation available") + "\n"

    elif _object.__class__.__name__ == "Runtime_Decorator":
        docstring = documentation(_object.function)
    else:
        docstring = documentation(type(_object))
        #raise ValueError("Unsupported object {} with type: {}".format(_object, type(_object)))
        
    return docstring

def function_names(function):
    return function.__code__.co_varnames            
        
def test_pack_unpack():
    ciphertext = "as;flkjasdf;lkjasfd"
    iv = "21209348afdso"
    tag = "zpx98yvzclkj"
    extra_data = "1x897=a[19njkS"
    
    packed = save_data(ciphertext, iv, tag, extra_data)
    _ciphertext, _iv, _tag, _extra_data = unpack_data(packed)
    assert _ciphertext == ciphertext
    assert _iv == iv
    assert _tag == tag
    assert _extra_data == extra_data             
    
def test_isancestor_isdescendant():
    descendant = objects["/Python/Rpc_Server/Rpc_Socket"]
    ancestor = objects["/Python"]
    assert isancestor(ancestor, descendant)
    assert isdescendant(descendant, ancestor)