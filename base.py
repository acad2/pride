""" Contains The root inheritance objects that provides many features of the package. """
              
import operator
import itertools
import sys
import heapq
import pprint
import inspect
from six import with_metaclass
       
import pride
import pride.metaclass
import pride.utilities
import pride.contextmanagers
import pride.module_utilities
from pride.errors import *
#objects = pride.objects

__all__ = ["DeleteError", "AddError", "load", "Base", "Reactor", "Wrapper", "Proxy"]

def rebuild_object(saved_data):
    """ usage: load(saved_data) => restored_instance, attributes """
    user = pride.objects["/User"]
    attributes = user.load_data(saved_data)
    repo_id = user.generate_tag(user.username)
    version_control = pride.objects["/Python/Version_Control"]
    _required_modules = []
    module_info = attributes.pop("_required_modules")
    class_name = module_info.pop()
    for module_name, module_id in module_info:
        source = version_control.load_module(module_name, module_id, repo_id)        
        module_object = pride.module_utilities.create_module(module_name, source)
        _required_modules.append((module_name, module_id, module_object))     
    
    self_class = getattr(module_object, class_name)
    attributes["_required_modules"] = _required_modules        
           
    self = self_class.__new__(self_class)
    return self, attributes
    
def restore_attributes(new_self, attributes):
    """ Loads and instance from a bytestream or file produced by pride.base.Base.save. 
        Currently being reimplemented"""
            
    saved_objects = attributes["objects"]
    objects = attributes["objects"] = {}
    
    for instance_type, saved_instances in saved_objects.items():         
        objects[instance_type] = [load(instance) for instance in saved_instances]
       
    attribute_modifier = attributes.pop("_attribute_type")
    for key, value in attributes.items():
        modifier = attribute_modifier.get(key, '')
        if modifier == "reference":       
            attributes[key] = pride.objects[value]
        elif modifier == "save":            
            attributes[key] = load(value)
            
    new_self.on_load(attributes)
    return new_self
          
def load(saved_object):
    new_self, attributes = rebuild_object(saved_object)
    return restore_attributes(new_self, attributes) 
        
class Base(with_metaclass(pride.metaclass.Metaclass, object)):  
    """ The root inheritance object. Provides many features:

    - When instantiating, arbitrary attributes may be assigned
          via keyword arguments
          
        - The class includes a defaults attribute, which is a dictionary
          of name:value pairs. These pairs will be assigned as attributes
          to new instances; Any attribute specified via keyword argument
          will override a default
                                  
        - A reference attribute, which provides access to the object from any context. 
            - References are human readable strings indicating the name of an object.
            - References are mapped to objects in the pride.objects dictionary.          
            - An example reference looks like "/Python/File_System". 
            - Initial objects have no number appended to the end. The 0 is implied.
                - Explicit is better then implicit, but for some objects, it 
                  makes no sense to have multiple copies, so enumerating them
                  accomplishes nothing.
            - Subsequent objects have an incrementing number appended to the end.
            
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
            - The verbosity class dictionary is the ideal place to store
              and dispatch alert levels, rather then hardcoding them.
              
        - Augmented docstrings. Information about class defaults
          and method names + argument signatures + method docstrings (if any)
          is included automatically when you print base_object.__doc__. 
         
        - Inherited class attributes. Attributes such as the class defaults
          dictionary are automatically inherited from their ancestor class.
            - This basically enables some syntatic sugar when declaring classes,
              in that defaults don't need to be declared as a copy of the ancestor
              classes defaults explicitly.             
            - Attributes that are inherited on all Base objects are: 
                - defaults
                - mutable_defaults
                - flags
                - verbosity
                - parser_ignore
                - required_attributes 
                - site_config_support
            - Supported attributes are extensible when defining new classes.
           
        - Site config support. Using the site_config module, the values of any
          accessible class attributes may be modified to customize the needs 
          of where the software is deployed. 
            - The attributes that are supported by default on all Base objects are:
                - defaults
                - mutable_defaults
                - flags
                - verbosity
            - This list is extensible when defining a new class
            
    Note that some features are facilitated by the metaclass. These include
    the argument parser, inherited class attributes, and documentation.
    
    How to use references
    ------------            
    Bad:
        
        my_base_object.other_base_object = other_base_object
        
    Good:
        
        my_base_object.add(other_base_object)
        
    Also good:
        
        my_base_object.other_base_object = other_base_object.reference
        
    In the first case, the other_base_object attribute stores a literal object in
    the objects __dict__. This is a problem because the environment has no way 
    of (efficiently) detecting that you have saved a reference to another 
    object when the object is simply assigned as an attribute. This can cause
    memory leaks when you try to delete other_base_object or my_base_object.
    
    In the second case, the add method is used to store the object. The add
    method performs reference tracking information so that when my_base_object is
    deleted, other_base_object will automatically be removed, eliminating reference
    problems which can/will cause one object or both to become uncollectable
    by the garbage collector.
    
    By default, the add method stores objects in the my_base_object.objects 
    dictionary. The add method is extensible, so for example, if your object
    has lots of one type of object added to it, you can simply append the
    object to a list in the add method, but remember to call the base class 
    add as well if you do (via super). This is because add does reference 
    tracking as well as storing the supplied object. You would then access the
    stored objects via enumerating the list you stored them all in and 
    operating on them in a batch.
    
    In the third case, the object is not saved, just the objects reference.
    This is good because it will avoid the hanging reference problem that can
    cause memory leaks. This will work well when my_base_object only has the one
    other_base_object to keep track of. other_base_object is then accessed by
    looking up the reference in the pride.objects dictionary."""
    
    # certain container type class attributes are "inherited" from base classes
    # these include defaults, required_attributes, mutable_defaults, verbosity
    # parser_ignore, and flags (all of which are explained below and above)
    # when subclassing, creating new class defaults will automatically merge the
    # newly specified defaults with the base class defaults, and similarly so for each 
    # attribute inherited this way.
    
    # the defaults attribute sets what attributes new instances will initialize with
    # they can be overridden when initialized an object via keyword arguments
    # PITFALL: do not use mutable objects as a default. use mutable_defaults instead
    defaults = {"deleted" : False, "dont_save" : False, "parse_args" : False,
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
    mutable_defaults = {}
    
    # defaults have a pitfall that can be a problem in certain cases;
    # because dictionaries are unordered, the order in which defaults
    # are assigned cannot be guaranteed. 
    # flags are guaranteed to be assigned before defaults.
    flags = {}
    
    # verbosity is an inherited class attribute used to store the verbosity
    # level of a particular message.
    verbosity = {"delete" : "vv", "initialized" : "vv", "remove" : "vv",
                 "add" : "vv", "update" : "v"}
    
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
    parser_ignore = ("replace_reference_on_load", "deleted",
                     "parse_args", "dont_save", "startup_components")    
        
    site_config_support = ("defaults", "verbosity", "flags", "mutable_defaults")        
    
    def _get_parent(self):
        return objects[self.parent_name] if self.parent_name else None
    parent = property(_get_parent)
   
    def _get_children(self):
        return (child for child in itertools.chain(*self.objects.values()) if child)
    children = property(_get_children)
    
    post_initializer = ''
    
    def __init__(self, **kwargs):               
        super(Base, self).__init__() # facilitates complicated inheritance - otherwise does nothing          
        self.references_to = []
        parent_name = self.parent_name = pride._last_creator
        instance_count = 0   
        _name = name = parent_name + "/" + self.__class__.__name__              
        while name in objects:
            instance_count += 1
            name = _name + str(instance_count)
        self._instance_count = instance_count
        self.reference = name
        objects[self.reference] = self        
            
        # the objects attribute keeps track of instances created by this self
        self.objects = {}

        for value, attributes in itertools.chain(self._localized_flags.items(), 
                                                 self._localized_defaults.items()):
            value = value[0]
            for attribute in attributes:
                setattr(self, attribute, value)             
        for value_type, attributes in self._localized_mutable_defaults.items():
            value_type = value_type[0]
            for attribute in attributes:
                setattr(self, attribute, value_type())
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        if self.parse_args:            
            command_line_args = self.parser.get_options()
            defaults = self.defaults
            for key, value in ((key, value) for key, value in
                                command_line_args.items() if 
                                value != defaults[key]):                
                setattr(self, key, value)

        if self.required_attributes:
            for attribute in self.required_attributes:
                try:
                    if not getattr(self, attribute):
                        raise ArgumentError("Required attribute '{}' has no value".format(attribute))
                except AttributeError:
                    import pprint
                    pprint.pprint(kwargs)
                    raise ArgumentError("Required attribute '{}' not assigned".format(attribute))
         
        if self.parent:            
            self.parent.add(self)
            
        if self.startup_components:
            for component_type in self.startup_components:
                component = self.create(component_type)
                setattr(self, component.__class__.__name__.lower(), 
                        component.reference)                         
        try:
            self.alert("Initialized", level=self.verbosity["initialized"])
        except (AttributeError, KeyError): 
            # Alert handler can not exist in some situations or not have its log yet
            pass
         
        if self.post_initializer:
            getattr(self, self.post_initializer)()
            
    def create(self, instance_type, *args, **kwargs):
        """ usage: object.create(instance_type, args, kwargs) => instance

            Given a type or string reference to a type and any arguments,
            return an instance of the specified type. The creating
            object will call .add on the created object, which
            performs reference tracking maintenance. 
            
            Returns the created object.
            Note, instance_type could conceivably be any callable, though a
            class is usually supplied. 
            
            If create is overloaded, ensure that ancestor create is called
            as well via super."""
        with pride.contextmanagers.backup(pride, "_last_creator"):
            pride._last_creator = self.reference
            try:
                instance = instance_type(*args, **kwargs)
            except TypeError:
                if isinstance(instance_type, type):
                    raise                
                instance = resolve_string(instance_type)(*args, **kwargs)        
        return instance
        
    def delete(self):
        """usage: object.delete()
            
            Explicitly delete a component. This calls remove and
            attempts to clear out known references to the object so that
            the object can be collected by the python garbage collector.
            
            The default alert level for object deletion is 'vv'
            
            If delete is overloaded, ensure that ancestor delete is called as
            well via super."""             
        self.alert("Deleting", level=self.verbosity["delete"])
        if self.deleted:            
            raise DeleteError("{} has already been deleted".format(self.reference))
            
        for child in list(self.children):
            try:
                child.delete()
            except DeleteError:
                if self.reference in child.references_to:
                    raise        
        
        if self.references_to:
            # make a copy, as remove will mutate self.references_to            
            for name in self.references_to[:]:
                objects[name].remove(self)            
        del objects[self.reference]
        self.deleted = True           
            
    def add(self, instance):
        """ usage: object.add(instance)

            Adds an object to caller.objects[instance.__class__.__name__] and
            notes the reference location.
            
            The default alert level for add is 'vv'
            
            Raises AddError if the supplied instance has already been added to
            this object.
            
            If overloading the add method, ensure super is called to invoke the
            ancestor version that performs bookkeeping.
            
            Make sure to overload remove if you modify add (if necessary)"""    
        self.alert("Adding: {}", (instance, ), level=self.verbosity["add"])
        self_objects = self.objects
        instance_class = type(instance).__name__
        try:
            siblings = self_objects[instance_class]
        except KeyError:
            self_objects[instance_class] = siblings = [instance]                         
        else:
            if instance in siblings:
                raise AddError    
            siblings.append(instance)
            
        instance.references_to.append(self.reference)          
        
    def remove(self, instance):
        """ Usage: object.remove(instance)
        
            Removes an instance from self.objects. Modifies object.objects
            and instance.references_to.
            
            The default alert level for object removal is 'vv'"""    
        self.alert("Removing {}", [instance], level=self.verbosity["remove"])  
        self.objects[type(instance).__name__].remove(instance)
        instance.references_to.remove(self.reference)                    
    
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
        
        An objects verbosity can be modified without modifying the source code
        via the site_config module.
        
        format_args can sometimes make alerts more readable, depending on the
        length of the message and the length of the format arguments.
            - It is arguably better to do: 
                [code]
                message = 'string stuff {} and more string stuff {}'.format(variable1, variable2)
                my_object.alert(message, level=level)[/code]""" 
        alert_handler = objects["/Alert_Handler"]               
        message = "{}: ".format(self.reference) + (message.format(*format_args) if format_args else message)
        if level in alert_handler._print_level or level is 0:                    
            sys.stdout.write(message + "\n")
            sys.stdout.flush()                           
        if level in alert_handler._log_level or level is 0:
            alert_handler.log.seek(0, 1) # windows might complain about files in + mode if this isn't done
            alert_handler.log.write(str(level) + message + "\n")    
                                                 
    def __getstate__(self):
        return self.__dict__.copy()
        
    def __setstate__(self, state):
        self.on_load(state)
              
    def __str__(self):
        return self.reference
        
    def save(self, _file=None):
        """ usage: base_object.save(_file=None)
            
            Saves the state of the calling objects __dict__. If _file is not
            specified, a pickled stream is returned. If _file is specified,
            the stream is written to the supplied file like object via 
            pickle.dump and then returned.
            
            This method and load are under being reimplemented"""        
        self.alert("Saving")
        attributes = self.__getstate__()
        self_objects = attributes.pop("objects", {})
        saved_objects = attributes["objects"] = {}
        found_objects = []
        for component_type, values in self_objects.items():
            saved_objects[component_type] = new_values = []
            for value in sorted(values, key=operator.attrgetter("reference")):
                if hasattr(value, "save"):
                    found_objects.append(value)
                    if not getattr(value, "dont_save", False):                           
                        new_values.append(value.save())

        attribute_type = attributes["_attribute_type"] = {}
        for key, value in attributes.items():
            if value in found_objects:
                attributes[key] = value.reference
                attribute_type[key] = "reference"
            elif hasattr(value, "save") and not getattr(value, "dont_save"):
                attributes[key] = value.save()
                attribute_type[key] = "saved"  
                
        required_modules = pride.module_utilities.get_all_modules_for_class(type(self))
        version_control = objects["/Python/Version_Control"]     
        user = objects["/User"]
        hash_function = user.generate_tag
        repo_id = hash_function(user.username)
        _required_modules = []
        for module_name, source, module_object in required_modules:            
            module_id = hash_function(source)
            version_control.save_module(module_name, source, module_id, repo_id)
            _required_modules.append((module_name, module_id))
            
        attributes["_required_modules"] = _required_modules + [self.__class__.__name__]        
        try:
            saved_data = pride.objects["/User"].save_data(attributes)
        except TypeError:
            self.alert("Unable to save attributes '{}'".format(pprint.pformat(attributes)), level=0)
            raise
            
        if _file:
            _file.write(saved_data)
        return saved_data            
            
    load = staticmethod(load)       
        
    def on_load(self, attributes):
        """ usage: base.on_load(attributes)
        
            Implements the behavior of an object after it has been loaded.
            This method may be extended by subclasses to customize 
            functionality for instances created by the load method. Often
            times this will implement similar functionality as the objects
            __init__ method does (i.e. opening a file or database).
            
            NOTE: Currently being reimplemented"""          
        [setattr(self, key, value) for key, value in attributes.items()]
                
        if self.replace_reference_on_load:
            print "Replacing instance", self
            pride.objects[self.reference] = self
            print "Done"
        self.alert("Loaded", level='v')
        
    def update(self, update_children=False, _already_updated=None):
        """usage: base_instance.update() => updated_base
        
           Reloads the module that defines base and returns an updated
           instance. The old component is replaced by the updated component
           in the environment. Further references to the object via 
           reference will be directed to the new, updated object. 
           Attributes of the original object will be assigned to the
           updated object.
           
           Note that modules are preserved when update is called. Any
           modules used in the updated class will not necessarily be the
           same as the modules in use in the current global scope.
           
           The default alert level for update is 'v'
           
           Potential pitfalls:
               
                - Classes that instantiate base objects as a class attribute
                  will produce an additional object each time the class is
                  updated. Solution: instantiate base objects in __init__ """
        self.alert("Beginning Update ({})...", (id(self), ), level=self.verbosity["update"])          
        _already_updated = _already_updated or [self.reference]
        class_base = pride.utilities.updated_class(type(self))        
        class_base._required_modules.append(self.__class__.__name__)        
        new_self = class_base.__new__(class_base)
        for attribute, value in ((key, value) for key, value in
                                 self.__dict__.items() if key not in
                                 self.__class__.__dict__):
            setattr(new_self, attribute, value)    
        if not hasattr(new_self, "reference"):
            new_self.reference = self.reference
        if not hasattr(new_self, "references_to"):
            new_self.references_to = self.references_to[:]
            
        assert "reference" not in self.__class__.__dict__, self.__class__.__dict__ 
        assert hasattr(self, "reference"), pprint.pformat(self.__dict__)
      #  assert "reference" in self.__dict__, pprint.pformat(self.__dict__.keys())
        assert hasattr(new_self, "reference"), pprint.pformat(new_self.__dict__)
        references = self.references_to[:]
        for reference in references:#self.references_to[:]:
            _object = pride.objects[reference]
            _object.remove(self)
        for reference in references:
            _object = pride.objects[reference]
            _object.add(new_self)
          
        pride.objects[self.reference] = new_self
        if update_children:
            for child in self.children:
                if child.reference not in _already_updated:                    
                    _already_updated.append(child.reference)
                    child.update(True, _already_updated)  
        self.alert("... Finished updating", level=0)
        return new_self
                
        
class Wrapper(Base):
    """ A wrapper to allow 'regular' python objects to function as a Base.
        The attributes on this wrapper will overload the attributes
        of the wrapped object. Any attributes not present on the wrapper object
        will be gotten from the underlying wrapped object. This class
        acts primarily as a wrapper and secondly as the wrapped object.
        This allows easy preemption/overloading/extension of methods by
        defining them.
        
        The class supports a "wrapped_object_name" attribute. When creating
        a new class of wrappers,  wrapped object can be made available as
        an attribute using the name given. If this attribute is not assigned,
        then the wrapped object can be accessed via the wrapped_object attribute"""
     
    defaults = {"wrapped_object" : None}
    
    wrapped_object_name = ''
    
    parser_ignore = ("wrapped_object", )
        
    def __init__(self, **kwargs):
        super(Wrapper, self).__init__(**kwargs)
        if self.wrapped_object_name:
            setattr(self, self.wrapped_object_name, self.wrapped_object)
            
    def __getattr__(self, attribute):        
        try:
            return getattr(self.wrapped_object, attribute)
        except AttributeError:
            raise AttributeError("'{}' object has no attribute '{}'".format(type(self).__name__, attribute))
                        
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
       the wrapped object and secondly as a Proxy object. This means that       
       Proxy attributes are get/set on the underlying wrapped object first,
       and if that object does not have the attribute or it cannot be
       assigned, the action is performed on the proxy instead. This
       prioritization is the opposite of the Wrapper class.
       
       This class also supports a wrapped_object_name attribute. See 
       Base.Wrapper for more information."""
    
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
        
        Attribute access on a static wrapper is faster then the regular wrapper. """
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
            