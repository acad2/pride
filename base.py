""" Contains The root inheritance objects that provides many features of the package. 
    An object that inherits from pride.base.Base will possess these capabilities:
        
        - When instantiating, arbitrary attributes may be assigned
          via keyword arguments
          
        - The class includes a defaults attribute, which is a dictionary
          of name:value pairs. These pairs will be assigned as attributes
          to new instances; Any attribute specified via keyword argument
          will override a default
        
        - An instance name, which provides a reference to the component from any context. 
          Instance names are mapped to instance objects in pride.objects.
          
        - The flag parse_args=True may be passed to the call to 
          instantiate a new object. If so, then the metaclass
          generated parser will be used to interpret command
          line arguments. Only command line arguments that are
          in the class defaults dictionary will be assigned to 
          the new instance. Arguments by default are supplied 
          explicitly with long flags in the form --attribute value.
          Arguments assigned via the command line will override 
          both defaults and any keyword arg specified values. 
          Consult the parser defintion for further information,
          including using short/positional args and ignoring attributes.
          
        - The methods create/delete, and add/remove:
            - The create method returns an instantiated object and
              calls add on it automatically. This performs book keeping
              with the environment regarding references and parent information.
            - The delete method is used to explicitly destroy a component.
              It calls remove internally to remove known locations
              where the object is stored and update any tracking 
              information in the environment
        
        - The alert method, which makes logging and statements 
          of varying verbosity simple and straight forward.
                    
        - Decorator(s) and monkey patches may be specified via
          keyword argument to any method call. Note that this
          functionality does not apply to python objects
          builtin magic methods (i.e. __init__). The syntax
          for this is:
          
            - component.method(decorator='module.Decorator')
            - component.method(decorators=['module.Decorator', ...])
            - component.method(monkey_patch='module.Method')
          
          The usage of these does not permanently wrap/replace the
          method. The decorator/patch is only applied when specified.
        
        - Augmented docstrings. Information about class defaults
          and method names + argument signatures + method docstrings (if any)
          is included automatically when you print base.__doc__. 
          
    Note that some features are facilitated by the metaclass. These include
    the argument parser, runtime decoration, and documentation.
    
    Instances of Base classes are counted and have an instance_name attribute.
    This is equal to type(instance).__name__ + str(instance_count). There
    is an exception to this; The first instance is number 0 and
    its name is simply type(instance).__name__, without 0 at the end.
    The instance_name can be used to reference the object from any scope, 
    as long as the component exists at runtime."""
import operator
       
import pride
import pride.metaclass
import pride.persistence
import pride.utilities

from pride.errors import *
objects = pride.objects

__all__ = ["DeleteError", "AddError", "load", "Base", "Reactor", "Wrapper", "Proxy"]

def load(attributes='', _file=None):
    """ Loads and instance from a bytestream or file produced by pride.base.Base.save. 
        This is a higher level method then pride.persistence.load."""
    assert attributes or _file
        
    new_self, attributes = pride.persistence.load(attributes, _file)
    print "Loading: ", repr(new_self)
    saved_objects = attributes["objects"]
    objects = attributes["objects"] = {}
    
    for instance_type, saved_instances in saved_objects.items(): 
        print '\t', repr(new_self), "Restoring: ", instance_type
        objects[instance_type] = [load(instance) for instance in saved_instances]
       # print '\t', repr(new_self), "Restored {} instances".format(len(objects[instance_type]))
    attribute_modifier = attributes.pop("_attribute_type")
    for key, value in attributes.items():
        modifier = attribute_modifier.get(key, '')
        if modifier == "reference":
            print "\tRestored reference: ", value
            attributes[key] = pride.objects[value]
        elif modifier == "save":
            print "\tLoading attribute: ", key
            attributes[key] = load(value)
            
    new_self.on_load(attributes)
    return new_self
        
class Base(object):

    __metaclass__ = pride.metaclass.Metaclass
                
    # certain container type class attributes are "inherited" from base classes
    # these include defaults, required_attributes, mutable_defaults, verbosity
    # parser_ignore, and flags (all of which are explained below)
    # when subclassing, creating new class defaults will automatically merge the
    # newly specified defaults with the base class defaults, and similarly so for each 
    # attribute inherited this way.
    
    # the defaults attribute sets what attributes new instances will initialize with
    # they can be overridden when initialized an object via keyword arguments
    # PITFALL: do not use mutable objects as a default. use mutable_defaults instead
    defaults = {"_deleted" : False, "dont_save" : False,
                "replace_reference_on_load" : True,
                "startup_components" : tuple()}   
    
    # if certain attributes must be passed explicitly, including them in the
    # required_attributes class attribute will automatically raise an 
    # ArgumentError when they are not supplied.
    required_attributes = tuple()
    
    # mutable objects should not be included as defaults attributes
    # for the same reason they should not be used as default arguments
    # the type associated with the attribute name will be instantiated with 
    # no arguments when the object initializes
    mutable_defaults = {} # {attribute_name : mutable_type}, i.e {'defaults' : dict}
    
    # verbosity is an inherited class attribute used to store the verbosity
    # level of a particular message.
    verbosity = {"delete" : 'vv', "initialized" : "vv"}
            
    # defaults have a pitfall that can be a problem in certain cases
    # because dictionaries are unordered, the order in which defaults
    # are assigned cannot be guaranteed. 
    # flags are guaranteed to be assigned before defaults, and in the order specified
    # flags should be a container of 2-tuples, which are attribute value pairs
    flags = {}.items() 
    
    # A command line argument parser is generated automatically for
    # every Base class based upon the attributes contained in the
    # class defaults dictionary. Specific attributes can be modified
    # or ignored by specifying them in class.parser_modifiers and
    # class.parser_ignore. 
    
    # parser modifiers are attribute : options pairs, where options
    # is a dictionary. The keys may include any keyword arguments 
    # that are used by argparse.ArgumentParser.add_argument. Most
    # relevent are the "types" and "nargs" options. types may be used 
    # to specify that the argument should be positional, -s short style,
    # or --long long style flags. nargs indicates the number of expected
    # arguments for the flag in question. Note that attributes default to 
    # using --long style flags.
    # exit_on_help determines whether or not to quit when the --help flag
    # is specified as a command line argument    
    parser_modifiers = {"exit_on_help" : True}    
    
    # names in parser_ignore will not be available as command line arguments
    parser_ignore = ("replace_reference_on_load", "_deleted",
                     "parse_args", "dont_save", "startup_components")    
    
    # an objects parent is the object that .create'd it.
    def _get_parent_name(self):
        return pride.environment.parents.get(self, 
                                             pride.environment.last_creator)     
    parent_name = property(_get_parent_name)
    
    def _get_parent(self):
        assert self.parent_name != self.instance_name
        return objects[self.parent_name]
    parent = property(_get_parent)
    
    def __init__(self, **kwargs):
        super(Base, self).__init__() # facilitates complicated inheritance - otherwise does nothing
        
        pride.environment.register(self) # acquire instance_name
        pride.environment.parents[self] = pride.environment.last_creator
        
        # the objects attribute keeps track of instances created by this self
        self.objects = {}
       
        attributes = self.defaults.copy()
        attributes.update(kwargs)
        if attributes.get("parse_args"):
            additional_attributes = {}
            command_line_args = self.parser.get_options()
            defaults = self.defaults
            attributes.update(dict((key, value) for key, value in 
                                    command_line_args.items() if 
                                    value != defaults[key]))  
        if self.flags:
            [setattr(self, attribute, value) for attribute, value in self.flags]
        if self.mutable_defaults:
            [setattr(self, attribute, value()) for attribute, value in self.mutable_defaults.items()]            
        [setattr(self, attribute, value) for attribute, value in attributes.items()]

        if self.startup_components:
            for component_type in self.startup_components:
                component = self.create(component_type)
                setattr(self, component.__class__.__name__.lower(), 
                        component.instance_name) 
        if self.required_attributes:
            for attribute in self.required_attributes:
                try:
                    if getattr(self, attribute) == self.defaults[attribute]:
                        raise ArgumentError("Required argument {} not supplied".format(attribute))
                except AttributeError:
                    raise ArgumentError("Required argument {} not supplied".format(attribute))
        try:
            self.alert("Initialized", level=self.verbosity["initialized"])
        except KeyError:
            pass
            
    def create(self, instance_type, *args, **kwargs):
        """ usage: object.create("module_name.object_name", 
                                args, kwargs) => instance

            Given a type or string reference to a type and any arguments,
            return an instance of the specified type. The creating
            object will call .add on the created object, which
            performs reference tracking maintainence. The object
            will be added to the environment if it is not yet in it.
            
            Use of the create method provides an instance_name
            reference to the instance. The instance does not need
            to be a Base object to receive an instance_name this way.
            Non Base objects can retrieve their instance name via
            up to two ways. If the object can have arbitrary attributes
            assigned, it will be provided with an instance_name attribute. 
            If not (i.e. __slots__ is defined), the instance_name can be
            obtained via the pride.environment.instance_name dictionary, 
            using the instance as the key."""
        self_name = self.instance_name
        backup = pride.environment.last_creator
        pride.environment.last_creator = self_name
        try:
            instance = instance_type(*args, **kwargs)
        except TypeError:
            if isinstance(instance_type, type):
                raise
            instance = resolve_string(instance_type)(*args, **kwargs)        

        pride.environment.parents[instance] = self_name
        if instance not in pride.environment.instance_name:
            pride.environment.register(instance)
        self.add(instance)
        pride.environment.last_creator = backup
        return instance

    def invoke(self, callable_string, *args, **kwargs):
        """ Calls the method specified in callable_string with args and kwargs.
            Objects that do not require any form of Base object functionality
            (such as an instance name) can be created via invoke instead of 
            the create method. """
        return resolve_string(callable_string)(*args, **kwargs)
        
    def delete(self):
        """usage: object.delete()
            
            Explicitly delete a component. This calls remove and
            attempts to clear out known references to the object so that
            the object can be collected by the python garbage collector"""
        self.alert("Deleting", level=self.verbosity["delete"])
        if self._deleted:
            raise DeleteError("{} has already been deleted".format(self.instance_name))
        pride.environment.delete(self)
        self._deleted = True
        
    def remove(self, instance):
        """ Usage: object.remove(instance)
        
            Removes an instance from self.objects. Modifies object.objects
            and environment.references_to."""
        #self.alert("Removing {}", [instance], level=0)
        try:
            self.objects[instance.__class__.__name__].remove(instance)
        except ValueError:
            print self, "Failed to remove: ", instance
            raise
        pride.environment.references_to[instance.instance_name].remove(self.instance_name)
        
    def add(self, instance):
        """ usage: object.add(instance)

            Adds an object to caller.objects[instance.__class__.__name__] and
            performs bookkeeping operations for the environment."""   
        
        objects = self.objects
        instance_class = instance.__class__.__name__
        siblings = objects.get(instance_class, [])#set())
        if instance in siblings:
            print self, instance, siblings
            raise AddError
        #siblings.add(instance)
        siblings.append(instance)
        objects[instance_class] = siblings      
                    
        instance_name = pride.environment.instance_name[instance]
        try:
            pride.environment.references_to[instance_name].add(self.instance_name)
        except KeyError:
            pride.environment.references_to[instance_name] = set((self.instance_name, ))      
            
    def alert(self, message, format_args=tuple(), level=0):
        """usage: base.alert(message, format_args=tuple(), level=0)

        Display/log a message according to the level given. The alert may 
        be printed for immediate attention and/or logged, depending on
        the current Alert_Handler print_level and log_level.

        - message is a string that will be logged and/or displayed
        - format_args are any string formatting args for message.format()
        - level is an integer indicating the severity of the alert.

        alert severity is relative to Alert_Handler log_level and print_level;
        a lower verbosity indicates a less verbose notification, while 0
        indicates a message that should not be suppressed. log_level and
        print_level may passed in as command line arguments to globally control verbosity.
        
        format_args can sometimes make alerts more readable, depending on the
        length of the message and the length of the format arguments."""
        return objects["->Alert_Handler"]._alert(self.instance_name + 
                                                 ": " + message, 
                                                 level, format_args)     
    def __getstate__(self):
        return self.__dict__.copy()
        
    def __setstate__(self, state):
        self.on_load(state)
              
    def __str__(self):
        return self.instance_name
        
    def save(self, attributes=None, _file=None):
        """ usage: base.save([attributes], [_file])
            
            Saves the state of the calling objects __dict__. If _file is not
            specified, a pickled stream is returned. If _file is specified,
            the stream is written to the supplied file like object via 
            pickle.dump.
            
            The attributes argument, if specified, should be a dictionary
            containing the attribute:value pairs to be pickled instead of 
            the objects __dict__.
            
            If the calling object is one that has been created via the update
            method, the returned state will include any required source code
            to rebuild the object."""
        self.alert("Saving")
        attributes = self.__getstate__()
        objects = attributes.pop("objects", {})
        saved_objects = attributes["objects"] = {}
        found_objects = []
        for component_type, values in objects.items():
            saved_objects[component_type] = new_values = []
            for value in sorted(values, key=operator.attrgetter("instance_name")):
                if hasattr(value, "save"):
                    found_objects.append(value)
                    if not getattr(value, "dont_save", False):   
                        new_values.append(value.save())

        attribute_type = attributes["_attribute_type"] = {}
        for key, value in attributes.items():
            if value in found_objects:
                attributes[key] = value.instance_name
                attribute_type[key] = "reference"
            elif hasattr(value, "save") and not getattr(value, "dont_save"):
                attributes[key] = value.save()
                attribute_type[key] = "saved"      
        return pride.persistence.save(self, attributes, _file)    
            
    load = staticmethod(load) # see base.load at beginning of file
        
    def on_load(self, attributes):
        """ usage: base.on_load(attributes)
        
            Implements the behavior of an object after it has been loaded.
            This method may be extended by subclasses to customize 
            functionality for instances created by the load method. Often
            times this will implement similar functionality as the objects
            __init__ method does (i.e. opening a file or database)."""     
        [setattr(self, key, value) for key, value in attributes.items()]
        pride.environment.add(self)
        
        if (self.replace_reference_on_load and 
            self.instance_name != attributes["instance_name"]):
            print "Replacing instance"
            pride.environment.replace(attributes["instance_name"], self)
            print "Done"
        self.alert("Loaded", level='v')
        
    def update(self):
        """usage: base_instance.update() => updated_base
        
           Reloads the module that defines base and returns an updated
           instance. The old component is replaced by the updated component
           in the environment. Further references to the object via 
           instance_name will be directed to the new, updated object. 
           Attributes of the original object will be assigned to the
           updated object.
           
           Note that modules are preserved when update is called. Any
           modules used in the updated class will not necessarily be the
           same as the modules in use in the current global scope."""
        self.alert("Updating", level='v') 
        
        class_base = pride.utilities.updated_class(type(self))
        class_base._required_modules.append(self.__class__.__name__)        
        new_self = class_base.__new__(class_base)
                
        # a mini replacement __init__
        attributes = new_self.defaults.copy()
        attributes["_required_modules"] = class_base._required_modules
        [setattr(new_self, key, value) for key, value in attributes.items()]
        pride.environment.add(new_self)        
        
        attributes = self.__dict__
        pride.environment.replace(self, new_self)
        [setattr(new_self, key, value) for key, value in attributes.items()]
        return new_self
                
        
class Wrapper(Base):
    """ A wrapper to allow 'regular' python objects to function as a Base.
        The attributes on this wrapper will overload the attributes
        of the wrapped object. Any attributes not present on the wrapper object
        will be gotten from the underlying wrapped object. This class
        acts primarily as a wrapper and secondly as the wrapped object.
        This allows easy preemption/overloading/extension of methods by
        defining them."""
     
    defaults = {"wrapped_object" : None}
    wrapped_object_name = ''
    
    parser_ignore = Base.parser_ignore + ("wrapped_object", )
        
    def __init__(self, **kwargs):
        super(Wrapper, self).__init__(**kwargs)
        if self.wrapped_object_name:
            setattr(self, self.wrapped_object_name, self.wrapped_object)
            
    def __getattr__(self, attribute):
     #   print repr(self), "Getting ", attribute, "From ", self.wrapped_object
        return getattr(self.wrapped_object, attribute)        
                        
    def wraps(self, _object):
        """ Sets the specified object as the object wrapped by this object. """
        assert _object is not self
        self.wrapped_object = _object
        if self.wrapped_object_name:
            setattr(self, self.wrapped_object_name, _object)
        
        
class Proxy(Base):
    """ usage: Proxy(wrapped_object=my_object) => proxied_object
    
       Produces an instance that will act as the object it wraps and as an
       Base object simultaneously. The object will act primarily as
       the wrapped object and secondly as a proxy object. This means that       
       Proxy attributes are get/set on the underlying wrapped object first,
       and if that object does not have the attribute or it cannot be
       assigned, the action is performed on the proxy instead. This
       prioritization is the opposite of the Wrapper class."""
    
    wrapped_object_name = ''
    
    def __init__(self, **kwargs):
        wraps = super(Proxy, self).__getattribute__("wraps")
        try:
            wrapped_object = kwargs.pop("wrapped_object")
        except KeyError:
            pass
        else:
            wraps(wrapped_object)
        super(Proxy, self).__init__(**kwargs)

    def wraps(self, _object):
        """ usage: wrapper.wraps(object)
            
            Makes the supplied object the object that is wrapped
            by the Proxy. """
        set_attr = super(Proxy, self).__setattr__
        set_attr("wrapped_object", _object)
        if self.wrapped_object_name:
            set_attr(self.wrapped_object_name, _object)
            
    def __getattribute__(self, attribute):
        try:
            wrapped_object = super(Proxy, self).__getattribute__("wrapped_object")
            value = super(type(wrapped_object), wrapped_object).__getattribute__(attribute)
        except AttributeError:
            value = super(Proxy, self).__getattribute__(attribute)
        return value

    def __setattr__(self, attribute, value):
        super_object = super(Proxy, self)
        try:
            wrapped_object = super_object.__getattribute__("wrapped_object")
            super(type(wrapped_object), wrapped_object).__setattr__(attribute, value)
        except AttributeError:
            super_object.__setattr__(attribute, value)
            
            
class Adapter(Base):
    """ Modifies the interface of the wrapped object. Effectively supplies
        the keys in the adaptations dictionary as attributes. The value 
        associated with that key in the dictionary is the corresponding
        attribute on the wrapped object that has the appropriate value. """
    adaptations = {}
    
    wrapped_object_name = ''
    
    def __init__(self, **kwargs):
        if "wrapped_object" in kwargs:
            self.wraps(kwargs.pop("wrapped_object"))
        else:
            self.wrapped_object = None
        super(Adapter, self).__init__(**kwargs)
            
    def wraps(self, _object):
        self.wrapped_object = _object
        if self.wrapped_object_name:
            setattr(self, self.wrapped_object_name, _object)
        
    def __getattribute__(self, attribute):
        get_attribute = super(Adapter, self).__getattribute__
        _attribute = get_attribute("adaptations").get(attribute, None)
        if _attribute is not None:
            result = getattr(get_attribute("wrapped_object"), _attribute)
        else:
            result = get_attribute(attribute)
        return result
        
    def __setattr__(self, attribute, value):
        get_attribute = super(Adapter, self).__getattribute__
        _attribute = get_attribute("adaptations").get(attribute, None)
        if _attribute is not None:
            setattr(self.wrapped_object, _attribute, value)
        else:
            super(Adapter, self).__setattr__(attribute, value)
        
        
class Static_Wrapper(Base):
    """ Wrapper that statically wraps attributes upon initialization. This
        differs from the default Wrapper in that changes made to the data of
        the wrapped object on a Wrapper will be reflected in the wrapper object
        itself. 
        
        With a Static_Wrapper, changes made to the wrapped objects attributes 
        will not be reflected in the Static_Wrapper object, unless the object
        is explicitly wrapped again using the wraps method.
        
        Attribute access on a static wrapper is faster then a dynamic wrapper. """
    wrapped_attributes = tuple()
    wrapped_object_name = ''
    
    defaults = {"wrapped_object" : None}
    
    def __init__(self, **kwargs):
        super(Static_Wrapper, self).__init__(**kwargs)
        if self.wrapped_object:
            self.wraps(self.wrapped_object)
            
    def wraps(self, _object):
        if self.wrapped_attributes:
            for attribute in self.wrapped_attributes:
                setattr(self, attribute, getattr(_object, attribute))
        else:
            for attribute in dir(_object):
                if "__" != attribute[:2] and "__" != attribute[:-2]:
                    setattr(self, attribute, getattr(_object, attribute))
                
        self.wrapped_object = _object
        if self.wrapped_object_name:
            setattr(self, self.wrapped_object_name, _object)        