""" Contains The root inheritance objects that provides many features of the package. 
    An object that inherits from mpre.base.Base will possess these capabilities:
        
        - When instantiating, arbitrary attributes may be assigned
          via keyword arguments
          
        - The class includes a defaults attribute, which is a dictionary
          of name:value pairs. These pairs will be assigned as attributes
          to new instances; Any attribute specified via keyword argument
          will override a default
          
        - An instance name, which provides a reference to the component from any context. 
          Instance names are mapped to instance objects in mpre.objects.
          
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
    This name associates the instance to the instance_name in the
    mpre.environment.objects. The instance_name can be used to reference
    the object from any scope, as long as the component exists at runtime."""
import operator
       
import mpre
import mpre.metaclass
import mpre.persistence
import mpre.utilities

from mpre.errors import *
objects = mpre.objects

__all__ = ["DeleteError", "AddError", "load", "Base", "Reactor", "Wrapper", "Proxy"]

def load(attributes='', _file=None):
    """ Loads and instance from a bytestream or file produced by mpre.base.Base.save. 
        This is a higher level method then mpre.persistence.load."""
    assert attributes or _file
        
    new_self, attributes = mpre.persistence.load(attributes, _file)
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
            attributes[key] = mpre.objects[value]
        elif modifier == "save":
            print "\tLoading attribute: ", key
            attributes[key] = load(value)
            
    new_self.on_load(attributes)
    return new_self
        
class Base(object):

    __metaclass__ = mpre.metaclass.Metaclass
                
    # the default attributes new instances will initialize with.
    defaults = {"_deleted" : False,
                "replace_reference_on_load" : True,
                "dont_save" : False,
                "delete_verbosity" : 'vv'}   
                
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
    parser_modifiers = {}    
    
    # names in parser_ignore will not be available as command line arguments
    parser_ignore = ("objects", "replace_reference_on_load", "_deleted",
                     "parse_args", "dont_save")
    # exit_on_help determines whether or not to quit when the --help flag
    # is specified as a command line argument
    exit_on_help = True
    
    # an objects parent is the object that .create'd it.
    def _get_parent_name(self):
        return mpre.environment.parents.get(self, mpre.environment.last_creator)
    parent_name = property(_get_parent_name)
    
    def _get_parent(self):
        return objects[self.parent_name]
    parent = property(_get_parent)
            
    def __init__(self, **kwargs):
        mpre.environment.add(self) # acquire instance_name
        # mutable datatypes (i.e. containers) should not be used inside the
        # defaults dictionary and should be set in the call to __init__   
        self.objects = {}
       
        attributes = self.defaults.copy()
        attributes.update(kwargs)
        if attributes.get("parse_args"):
            additional_attributes = {}
            command_line_args = self.parser.get_options()
            defaults = self.defaults
            attributes.update(dict((key, value) for key, value in 
                                    command_line_args.items() if value != defaults[key]))     
        [setattr(self, attr, val) for attr, val in attributes.items()]            

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
            obtained via the mpre.environment.instance_name dictionary, 
            using the instance as the key."""
        self_name = self.instance_name
        mpre.environment.last_creator = self_name
        try:
            instance = instance_type(*args, **kwargs)
        except TypeError:
            if isinstance(instance_type, type):
                raise
            instance = mpre.utilities.resolve_string(instance_type)(*args, **kwargs)        

        if instance not in mpre.environment.instance_name:
            mpre.environment.add(instance)
        self.add(instance)
        mpre.environment.parents[instance] = self_name
        return instance

    def delete(self):
        """usage: object.delete()
            
            Explicitly delete a component. This calls remove and
            attempts to clear out known references to the object so that
            the object can be collected by the python garbage collector"""
        self.alert("Deleting", level=self.delete_verbosity)
        if self._deleted:
            raise DeleteError("{} has already been deleted".format(self.instance_name))
        mpre.environment.delete(self)
        self._deleted = True
        
    def remove(self, instance):
        """ Usage: object.remove(instance)
        
            Removes an instance from self.objects. Modifies object.objects
            and environment.references_to."""
        #self.alert("Removing {}", [instance], level=0)
        try:
            self.objects[instance.__class__.__name__].remove(instance)
        except:
            print self, "Failed to remove: ", instance
            raise
        mpre.environment.references_to[instance.instance_name].remove(self.instance_name)
        
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
                    
        instance_name = mpre.environment.instance_name[instance]
        try:
            mpre.environment.references_to[instance_name].add(self.instance_name)
        except KeyError:
            mpre.environment.references_to[instance_name] = set((self.instance_name, ))      
            
    def alert(self, message="Unspecified alert message", format_args=tuple(), level=''):
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
        message = (self.instance_name + ": " + message.format(*format_args) if
                   format_args else self.instance_name + ": " + message)
        return objects["Alert_Handler"]._alert(message, level)            
                                                       
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
        return mpre.persistence.save(self, attributes, _file)    
            
    load = staticmethod(load) # see base.load at beginning of file
        
    def on_load(self, attributes):
        """ usage: base.on_load(attributes)
        
            Implements the behavior of an object after it has been loaded.
            This method may be extended by subclasses to customize 
            functionality for instances created by the load method. Often
            times this will implement similar functionality as the objects
            __init__ method does (i.e. opening a file or database)."""     
        [setattr(self, key, value) for key, value in attributes.items()]
        mpre.environment.add(self)
        
        if (self.replace_reference_on_load and 
            self.instance_name != attributes["instance_name"]):
            mpre.environment.replace(attributes["instance_name"], self)
            
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
        
        class_base = mpre.utilities.updated_class(type(self))
        class_base._required_modules.append(self.__class__.__name__)        
        new_self = class_base.__new__(class_base)
                
        # a mini replacement __init__
        attributes = new_self.defaults.copy()
        attributes["_required_modules"] = class_base._required_modules
        [setattr(new_self, key, value) for key, value in attributes.items()]
        mpre.environment.add(new_self)        
        
        attributes = self.__dict__
        mpre.environment.replace(self, new_self)
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
     
    defaults = Base.defaults.copy()
    defaults.update({"wrapped_object" : None})
    wrapped_object_name = ''
    
    parser_ignore = Base.parser_ignore + ("wrapped_object", )
        
    def __init__(self, **kwargs):
        super(Wrapper, self).__init__(**kwargs)
        if self.wrapped_object_name:
            setattr(self, self.wrapped_object_name, self.wrapped_object)
            
    def __getattr__(self, attribute):
        return getattr(self.wrapped_object, attribute)        
                        
    def wraps(self, _object):
        """ Sets the specified object as the object wrapped by this object. """
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

    defaults = Base.defaults.copy()
    
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

    def wraps(self, _object, set_defaults=False):
        """ usage: wrapper.wraps(object)
            
            Makes the supplied object the object that is wrapped
            by the calling wrapper. If the optional set_defaults
            attribute is True, then the wrapped objects class
            defaults will be applied."""
        set_attr = super(Proxy, self).__setattr__
        if set_defaults:
            for attribute, value in self.defaults.items():
                set_attr(attribute, value)
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