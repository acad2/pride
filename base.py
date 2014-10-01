from weakref import proxy, ref
import inspect
from sys import modules
import functools
import defaults


class Docstring(object):
    
    def __init__(self):
        super(Docstring, self).__init__()
        
    def __get__(self, instance, _class):
        options_text = '\n Default values for newly created instances:\n'     
        try: # gather the default attribute names and values
            options = ""
            for key, value in _class.defaults.items():
                options += " \t%s\t%s\n" % (key, value)
            if not options:
                options_text = "\n No defaults are assigned to new instances\n"
            else:
                options_text += options
        except KeyError: # does not have defaults
            options_text = "\n No class.defaults detected\n"
        docstring = "%s:\n" % _class.__name__
        class_docstring = getattr(_class, "__doc")
        docstring += "\t"+class_docstring+"\n"+options_text+"\n"
        docstring += " This object defines the following public methods:\n"
        count = 0
        found = False
        uses_decorator = False
        for attribute_name in _class.__dict__.keys():
            if "_" != attribute_name[0]:
                attribute = getattr(_class, attribute_name)
                if callable(attribute):
                    found = True
                    count += 1
                    count_string = str(count)        
                    docstring += " \t"+count_string+". "+attribute_name+", which uses the following argument specification:\n"
                    argspec = inspect.getargspec(attribute)
                    if argspec.args:
                        docstring += " \t\tRequired arguments: " + str(argspec.args) + "\n"
                    if argspec.defaults:
                        docstring += " \t\tDefault arguments: " + str(argspec.defaults) + "\n"
                    if argspec.varargs:
                        docstring += " \t\tVariable positional arguments: " + str(argspec.varargs)+ "\n"
                    if argspec.keywords:
                        docstring += " \t\tKeyword arguments: " + str(argspec.keywords) + "\n"""
        if not found:
            docstring += " \tNo public methods defined\n"
        docstring += "\n This objects method resolution order/class hierarchy is:\n \t"
        docstring += str(_class.__mro__)
        return docstring
                

class Metaclass(type):
    """Includes class.defaults attribute/values in docstrings."""
    
    def __new__(cls, name, bases, attributes):
        try:
            docstring = attributes["__doc__"]
        except KeyError:
            docstring = "No docstring found. Only introspected information available\n"
        attributes["__doc"] = docstring
        attributes["__doc__"] = Docstring()
        new_class = type.__new__(cls, name, bases, attributes)
        return new_class
            

class Base(object):
    """A base object to inherit from. an object that inherits from base 
    can have arbitrary attributes set upon object instantiation by specifying 
    argument tuples of (attribute_name, value) pairs or more readable as keyword arguments.
    an object that inherits from base will also be able to create/hold arbitrary 
    python objects by specifying them as arguments to create.
    
    classes that inherit from base should specify a class.defaults dictionary that will automatically
    include the specified (attribute, value) pairs on all new instances"""
    __metaclass__ = Metaclass
    
    # the default attributes an instance will initialize with.
    # storing them here makes them modifiable at runtime.
    defaults = defaults.Base
        
    # hotkeys should be pygame.locals.key_constant : eventlibrary.Event pairs
    hotkeys = {}
        
    def __init__(self, *args, **kwargs):
        super(Base, self).__init__()
        attributes = tuple(self.defaults.items()) + args
        self.attribute_setter(*attributes, **kwargs)
        # mutable datatypes (i.e. containers) should not be used inside the
        # defaults dictionary and should be set in the __init__, like so
        self.objects = {}        
    
    #def __getattribute__(self, attribute):  
    #    value = super(Base, self).__getattribute__(attribute)
    #    if "__" not in attribute and callable(value):
    #        value = Runtime_Decorator(value)
    #    return value
        
    def attribute_setter(self, *args, **kwargs):
        """usage: object.attribute_setter((name, value_pairs), attrs=values)
        
        sets instance attributes. positional arguments should be tuples that contain
        attribute_name, attribute_value pairs. keyword arguments can also be used
        to explicitly specify attributes. this is called implicitly in __init__ for any
        object that inherits from Base."""
        if args: 
            [setattr(self, attribute, value) for attribute, value in args]
        [setattr(self, attr, val) for attr, val in kwargs.items()]
                     
    def create(self, instance_type, *args, **kwargs): 
        """usage: object.create("module_name.object_name", args, kwargs)
        
        The specified python object will be instantiated with the given arguments
        and placed inside object.objects under the created objects class name via 
        the add method"""
        if not kwargs.has_key("parent"):
            kwargs["parent"] = proxy(self)
            kwargs["parent_weakref"] = ref(self)
            
        # resolve string to actual class
        if type(instance_type) == str:
            try:
                module, _class = instance_type.split(".")
            except ValueError:
                module, _class = __name__, instance_type
            finally:
                try:
                    module = modules[module]
                except KeyError:
                    module = __import__(module)
                instance_type = getattr(module, _class)
        
        # instantiate the new object from a class object
        # if the object does not accept the attempted supplied kwargs (such as
        # the above-set parent attribute), then it is wrapped so it can
        try:
            #print "attempting to instantiate", instance_type, args, kwargs
            instance = instance_type(*args, **kwargs)
        except:
            raise
            self.warning("Failed to instantiate %s, wrapping" % instance_type, "Notification:")
            instance = instance_type(*args)
            instance = Wrapper(instance, **kwargs)
        self.add(instance)
        return instance
        
    def add(self, instance):
        """usage: object.add(other_object)

        adds an already existing object to the instances' class name entry in parent.objects.
        """
        if not hasattr(instance, "parent"):
            instance.parent = self # is a reference problem without stm in place
        try:
            self.objects[instance.__class__.__name__].append(instance)
        except KeyError:
            self.objects[instance.__class__.__name__] = [instance]
        
    def delete(self, *args):
        """usage: object.delete() or object.delete(child)
        
        currently does not always function as intended. don't rely on it!"""
        if not args:     
            for child in self.get_children():
                child.delete()
            self.parent.objects[self.__class__.__name__].remove(self)
        else:
            for arg in args:
                arg.delete()

    def warning(self, message="Error_Code", level="Warning", callback=None, callback_event=None):
        """usage: object.warning(Message, level, callback)
        
        print a warning message to the console. the message will be prefixed by
        the severity of the error, which can be specified via the level argument.
        a callback_event can be supplied, which should be an eventlibrary.Event"""
        print level, message
        
        if callback_event:
            callback_event.post()
        if callback:
            function, args, kwargs = callback
            return function(*args, **kwargs)
            
    def get_children(self):
        """usage: for child in object.get_children...
        
        Creates a generator that yields the immediate children of the object."""
        for _list in self.objects.values():
            for child in _list:
                yield child
                
    def get_family_tree(self):
        """usage: all_objects = object.get_family_tree()
        
        returns a dictionary containing all the children/descendants of object"""
        tree = {self : []}
        for instance in self.get_children():
            tree[self].append(proxy(instance))
            tree.update(instance.get_family_tree())
        return tree    
    

#@functools.wraps # metadata would be nice...      
class Wrapper(Base):
    """a class that will act as the object it wraps and as a base
    object simultaneously."""
       
    def __init__(self, wrapped_object, *args, **kwargs):
        self.wrapped_object = None
        attr_setter = super(Wrapper, self).__getattribute__("attribute_setter")
        defaults = super(Wrapper, self).__getattribute__("defaults")
        try:
            attr_setter(defaults.items(), wrapped_object=wrapped_object, objects={}, *args, **kwargs)
        except:
            raise
                       
    def _get_wrapper_attribute(self, attribute):
        return super(Wrapper, self).__getattribute__(attribute)

    def __getattribute__(self, attribute): 
        wrapped_object = super(Wrapper, self).__getattribute__("wrapped_object")
        try:
            attr = getattr(wrapped_object, attribute)
        except AttributeError:
            try:
                attr = super(Wrapper, self).__getattribute__(attribute)
            except AttributeError:
                raise
        return attr
            
    def __setattr__(self, attribute, value):      
        try:
            wrapped_object = super(Wrapper, self).__getattribute__("wrapped_object")
            super(type(wrapped_object), wrapped_object).__setattr__(attribute, value)
        except AttributeError:
            super(Wrapper, self).__setattr__(attribute, value)
            
    def __dir__(self):
        return dir(super(Wrapper, self).__getattribute__("wrapped_object"))

    def __str__(self):
        try:
            name = str(super(Wrapper, self).__getattribute__("wrapped_object"))
        except AttributeError:
            name = ""
        return "Wrapped(%s)" % name

    def __repr__(self):
        return super(Wrapper, self).__repr__()

    def __iter__(self):
        return self.wrapped_object
    
    def next(self): # python 2
        return next(self.wrapped_object)
        
    def __next__(self): # python 3
        return next(self.wrapped_object)
        
    def attribute_setter(self, *args, **kwargs):
        # modified version of base.attribute_setter using super calls to set
        # attributes on the wrapper instead of the wrapped object
        if args:
            for arg in args:
                for attribute, value in arg:
                    super(Wrapper, self).__setattr__(attribute, value)

        [super(Wrapper, self).__setattr__(attribute, value) for attribute, value in kwargs.items()]
        

class Process(Base):
    """a base process for processes to subclass from. Processes are managed
    by the system. The start method begins a process while the run method contains
    the actual code to be executed every frame."""
    
    defaults = defaults.Process
    
    def __init__(self, *args, **kwargs):
        self.args = tuple()
        self.kwargs = dict()
        super(Process, self).__init__(*args, **kwargs)
        Event = modules["eventlibrary"].Event
        if self.auto_start:
            Event(self.__class__.__name__, "start").post()
    
    def start(self): # compatibility with multiprocessing.Process
        self.run()
            
    def run(self):
        Event = modules["eventlibrary"].Event
        if self.target:
            self.target(*self.args, **self.kwargs)
        if self.recurring:        
            Event(self.__class__.__name__, "run").post()
        else:
            Event("System", "delete", self).post()
 
 
class Thread(Base):
    """does not run in psuedo-parallel like threading.thread"""
    defaults = defaults.Thread 
                
    def __init__(self, *args, **kwargs):
        self.args = tuple()
        self.kwargs = dict()
        self.results = []
        super(Thread, self).__init__(*args, **kwargs)
                
    def start(self):
        self.run()
    
    def run(self): 
        return self.function(*self.args, **self.kwargs)

        
# for machinelibrary.Machines
class Hardware_Device(Base):
    
    defaults = defaults.Hardware_Device
    
    def __init__(self, *args, **kwargs):
        super(Hardware_Device, self).__init__(*args, **kwargs)
        
         
class Runtime_Decorator(object):
    """provides the ability to call a function with a decorator specified via
    keyword argument.
    
    example: my_function(my_argument1, decorator="decoratorlibary.Tracer")"""
    
    def __init__(self, function):
        self.function = function
            
    def __call__(self, *args, **kwargs):
        
        #if kwargs.has_key("context_manager"):
        #    module_name, context_manager_name = self._resolve_string(kwargs.pop("context_manager"))
        if kwargs.has_key("monkey_patch"):
            module_name, patch_name = self._resolve_string(kwargs.pop("monkey_patch"))
            module = self._get_module(module_name)
            monkey_patch = getattr(module, patch_name)
            return monkey_patch(self.function.im_self, *args, **kwargs)
            
        if kwargs.has_key('decorator'):
            decorator_type = str(kwargs['decorator']) # string value of kwargs['decorator']
            
            module_name, decorator_name = self._resolve_string(decorator_type)
            decorator = self._get_decorator(decorator_name, module_name)
            wrapped_function = decorator(self.function)
            del kwargs['decorator']
            return wrapped_function(*args, **kwargs)

        elif kwargs.has_key('decorators'):
            decorators = []

            for item in kwargs['decorators']:
                module_name, decorator_name = self._resolve_string(item)
                decorator = self._get_decorator(decorator_name, module_name)
                decorators.append(decorator)

            wrapped_function = self.function
            for item in reversed(decorators):
                wrapped_function = item(wrapped_function)
            del kwargs['decorators']
            return wrapped_function(*args, **kwargs)

        else:
            return self.function(*args, **kwargs)

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
            module = modules[module_name]
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