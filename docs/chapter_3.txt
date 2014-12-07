Metaclasses

In CPython, classes are themselves objects. We just learned that objects
are constructed via the __new__ method. So we might ask the, if classes
are objects, and objects are created via the __new__ method, what calls
this method and creates a class?

A Metaclass is a class that is responsible for creating classes. The builtin
metaclass that is the default class constructor for all classes is the type
object we used at the end of chapter one to programmatically define classes:
    
    >>> new_class = type("New_Class", (object, ), {})
    >>> new_object = new_class()
    
It is possible to subclass from type and create a new metaclass that has
extended functionality. Remember how I mentioned that the use cases for
the __new__ method were pretty limited? Well, the use case for metaclasses is
even more so - they are relatively complicated beasts and should only be used
when it is not possible to accomplish something otherwise (which it almost always
is). They are only necessary if what you need to accomplish needs to be done 
after a class definition is laid out but before the class is actually constructed.

Consider the following decorator. It parses keyword arguments looking for
"decorator=" and does the work to apply the specified decorator:

class Runtime_Decorator(object):
    
    def __init__(self, function):
        self.function = function        
    
    def __call__(self, *args, **kwargs):
        #print self.function, args, kwargs            
        if kwargs.has_key('decorator'):
            decorator_type = str(kwargs['decorator']) # string value of kwargs['decorator']
            
            module_name, decorator_name = self._resolve_string(decorator_type)
            decorator = self._get_decorator(decorator_name, module_name)
            wrapped_function = decorator(self.function)
            del kwargs['decorator']
            return wrapped_function(*args, **kwargs)
        else:
            self.function(*args, **kwargs)
            
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
        try: # attempt to procure the decorator class
            decorator_wrap = getattr(module, decorator_name)
        except AttributeError: # decorator not found in module
            print("failed to locate decorators %s for function %s." %\
            (decorator_name, self.function))
        else:
            return decorator_wrap # instantiate the class with self.function

If you were to apply this decorator the traditional way:
            
    @Runtime_Decorator
    def method(self, *args, **kwargs):
        ...
        
However, if you want this functionality on all the methods of your class, you
would have to place @Runtime_Decorator in front of every definition. This involves
repetition, which means we should look for a way to programmaticaly do such a thing.

We can accomplish this using a metaclass:
    
    class Metaclass(type):
    """Includes class.defaults attribute/values in docstrings."""
    
    parser = argparse.ArgumentParser(description="Base parser", add_help=False)
    subparsers = parser.add_subparsers(help='')
    
    def __new__(cls, name, bases, attributes):
        Metaclass.make_docstring(attributes)
        Metaclass.make_parser(cls, attributes)
        attributes["instance_tracker"] = {}
        attributes["instance_count"] = 0
        new_class = type.__new__(cls, name, bases, attributes)
        Metaclass.decorate(cls, new_class, attributes)

        return new_class
        
    @staticmethod
    def decorate(cls, new_class, attributes):
        for key, value in new_class.__dict__.items():
            if key[0] != "_" and callable(value):
                setattr(new_class, key, MethodType(Runtime_Decorator(value), None, new_class))
        return new_class