from inspect import getmembers, ismethod

def get_methods(object):
    """returns a list of the objects callable methods"""
    return getmembers(object, predicate=ismethod)
        
def callattr(object, attribute, *args, **kwargs):
    """essentially: if object has attribute x, call it with args and kwargs. if not, return False.

    example: callattr(list, "append", 'text')"""

    func = getattr(object, attribute, None)

    if func:
        return func(*args, **kwargs)

def callattr2(object, attribute, *args, **kwargs):
    """essentially: if object has attribute x, call it with args and kwargs. if not, return False.

    different way of doing callattr"""

    func = object.__dict__.get('attribute')
    if func:
        return func(*args, **kwargs)

def function_printer(function):
    if function is not None:
        try:
            code = function.func_code
            code = code.co_name+str(code.co_varnames)+str(code.co_names)+str(code.co_freevars)
        except AttributeError:
            code = function
        finally:
            return code