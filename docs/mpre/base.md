mpre.base
==============

 Contains The root inheritance objects that provides many features of the package. 
    An object that inherits from mpre.base.Base will possess these capabilities:
        
        - When instantiating, arbitrary attributes may be assigned
          via keyword arguments
          
        - The class includes a defaults attribute, which is a dictionary
          of name:value pairs. These pairs will be assigned as attributes
          to new instances; Any attribute specified via keyword argument
          will override a default
          
        - An instance name, which provides a reference to the component from any context. 
          Instance names are mapped to instance objects in mpre.components.
          
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
    mpre.environment.components. The instance_name can be used to reference
    the object from any scope, as long as the component exists at runtime.

AddError
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.errors.AddError'>,
	 <type 'exceptions.ReferenceError'>,
	 <type 'exceptions.StandardError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

ArgumentError
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.errors.ArgumentError'>,
	 <type 'exceptions.TypeError'>,
	 <type 'exceptions.StandardError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

Base
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.base.Base'>, <type 'object'>)

- **load**(attributes, _file):

		 Loads and instance from a bytestream or file produced by mpre.base.Base.save. 
        This is a higher level method then mpre.persistence.load.


- **update**(self):

		usage: base_instance.update() => updated_base
        
           Reloads the module that defines base and returns an updated instance. The
           old component is replaced by the updated component in the environment.
           Further references to the object via instance_name will be directed to the
           new, updated object. Attributes of the original object will be assigned
           to the updated object.


- **alert**(self, message, format_args, level):

		usage: base.alert(message, format_args=tuple(), level=0)

        Display/log a message according to the level given. The alert may be printed
        for immediate attention and/or logged quietly for later viewing.

        -message is a string that will be logged and/or displayed
        -format_args are any string formatting args for message.format()
        -level is an integer indicating the severity of the alert.

        alert severity is relative to Alert_Handler log_level and print_level;
        a lower verbosity indicates a less verbose notification, while 0 indicates
        a message that should not be suppressed. log_level and print_level
        may passed in as command line arguments to globally control verbosity.


- **set_attributes**(self, **kwargs):

		 usage: object.set_attributes(attr1=value1, attr2=value2).
            
            Each key:value pair specified as keyword arguments will be
            assigned as attributes of the calling object. Keys are string
            attribute names and the corresponding values can be anything.
            
            This is called implicitly in __init__ for Base objects.


- **on_load**(self, attributes):

		 usage: base.on_load(attributes)
        
            Implements the behavior of an object after it has been loaded. This method 
            may be extended by subclasses to customize functionality for instances created
            by the load method.


- **create**(self, instance_type, *args, **kwargs):

		 usage: object.create("module_name.object_name", 
                                args, kwargs) => instance

            Given a type or string reference to a type, and arguments,
            return an instance of the specified type. The creating
            object will call .add on the created object, which
            performs reference tracking maintainence. 
            
            Use of the create method over direct instantiation can allow even 
            'regular' python objects to have a reference and be usable via parallel_methods 
            and Instruction objects.


- **remove**(self, instance):

		 Usage: object.remove(instance)
        
            Removes an instance from self.objects. Modifies object.objects
            and environment.references_to.


- **add**(self, instance):

		 usage: object.add(instance)

            Adds an object to caller.objects[instance.__class__.__name__] and
            performs bookkeeping operations for the environment.


- **save**(self, attributes, _file):

		 usage: base.save([attributes], [_file])
            
            Saves the state of the calling objects __dict__. If _file is not specified,
            a pickled stream is returned. If _file is specified, the stream is written
            to the supplied file like object via pickle.dump.
            
            The attributes argument, if specified, should be a dictionary containing 
            the attribute:value pairs to be pickled instead of the objects __dict__.
            
            If the calling object is one that has been created via the update method, the 
            returned state will include any required source code to rebuild the object.


- **delete**(self):

		usage: object.delete()
            
            Explicitly delete a component. This calls remove and
            attempts to clear out known references to the object so that
            the object can be collected by the python garbage collector


CorruptPickleError
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.errors.CorruptPickleError'>,
	 <class 'pickle.UnpicklingError'>,
	 <class 'pickle.PickleError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

DeleteError
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.errors.DeleteError'>,
	 <type 'exceptions.ReferenceError'>,
	 <type 'exceptions.StandardError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

Proxy
--------------

	 usage: Proxy(wrapped_object=my_object) => proxied_object
    
       Produces an instance that will act as the object it wraps and as an
       Base object simultaneously. The object will act primarily as
       the wrapped object and secondly as a proxy object. This means that       
       Proxy attributes are get/set on the underlying wrapped object first,
       and if that object does not have the attribute or it cannot be
       assigned, the action is performed on the proxy instead. This
       prioritization is the opposite of the Wrapper class.


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.base.Proxy'>, <class 'mpre.base.Base'>, <type 'object'>)

- **wraps**(self, obj, set_defaults):

		 usage: wrapper.wraps(object)
            
            Makes the supplied object the object that is wrapped
            by the calling wrapper. If the optional set_defaults
            attribute is True, then the wrapped objects class
            defaults will be applied.


UpdateError
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.errors.UpdateError'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

Wrapper
--------------

	 A wrapper to allow 'regular' python objects to function as a Base.
        The attributes on this wrapper will overload the attributes
        of the wrapped object. Any attributes not present on the wrapper object
        will be gotten from the underlying wrapped object. This class
        acts primarily as a wrapper and secondly as the wrapped object.


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'replace_reference_on_load': True,
	 'verbosity': '',
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.base.Wrapper'>, <class 'mpre.base.Base'>, <type 'object'>)

- **wraps**(self, _object):

				No documentation available


load
--------------

**load**(attributes, _file):

		 Loads and instance from a bytestream or file produced by mpre.base.Base.save. 
        This is a higher level method then mpre.persistence.load.
