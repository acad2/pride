pride.base
==============

 Contains The root inheritance objects that provides many features of the package. 

Adapter
--------------

	 Modifies the interface of the wrapped object. Effectively supplies
        the keys in the adaptations dictionary as attributes. The value 
        associated with that key in the dictionary is the corresponding
        attribute on the wrapped object that has the appropriate value. 


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.base.Adapter'>, <class 'pride.base.Base'>, <type 'object'>)

- **wraps**(self, _object):

				No documentation available


AddError
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.AddError'>,
	 <type 'exceptions.ReferenceError'>,
	 <type 'exceptions.StandardError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

ArgumentError
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.ArgumentError'>,
	 <type 'exceptions.TypeError'>,
	 <type 'exceptions.StandardError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

Base
--------------

	 The root inheritance object. Provides many features:

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
    looking up the reference in the pride.objects dictionary.


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.base.Base'>, <type 'object'>)

- **load**(saved_object):

				No documentation available


- **update**(self, update_children, _already_updated):

		usage: base_instance.update() => updated_base
        
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
                  updated. Solution: instantiate base objects in __init__ 


- **alert**(self, message, format_args, level):

		usage: base.alert(message, format_args=tuple(), level=0)

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
                my_object.alert(message, level=level)[/code]


- **on_load**(self, attributes):

		 usage: base.on_load(attributes)
        
            Implements the behavior of an object after it has been loaded.
            This method may be extended by subclasses to customize 
            functionality for instances created by the load method. Often
            times this will implement similar functionality as the objects
            __init__ method does (i.e. opening a file or database).
            
            NOTE: Currently being reimplemented


- **create**(self, instance_type, *args, **kwargs):

		 usage: object.create(instance_type, args, kwargs) => instance

            Given a type or string reference to a type and any arguments,
            return an instance of the specified type. The creating
            object will call .add on the created object, which
            performs reference tracking maintenance. 
            
            Returns the created object.
            Note, instance_type could conceivably be any callable, though a
            class is usually supplied. 
            
            If create is overloaded, ensure that ancestor create is called
            as well via super.


- **remove**(self, instance):

		 Usage: object.remove(instance)
        
            Removes an instance from self.objects. Modifies object.objects
            and instance.references_to.
            
            The default alert level for object removal is 'vv'


- **add**(self, instance):

		 usage: object.add(instance)

            Adds an object to caller.objects[instance.__class__.__name__] and
            notes the reference location.
            
            The default alert level for add is 'vv'
            
            Raises AddError if the supplied instance has already been added to
            this object.
            
            If overloading the add method, ensure super is called to invoke the
            ancestor version that performs bookkeeping.
            
            Make sure to overload remove if you modify add (if necessary)


- **save**(self, _file):

		 usage: base_object.save(_file=None)
            
            Saves the state of the calling objects __dict__. If _file is not
            specified, a pickled stream is returned. If _file is specified,
            the stream is written to the supplied file like object via 
            pickle.dump and then returned.
            
            This method and load are under being reimplemented


- **delete**(self):

		usage: object.delete()
            
            Explicitly delete a component. This calls remove and
            attempts to clear out known references to the object so that
            the object can be collected by the python garbage collector.
            
            The default alert level for object deletion is 'vv'
            
            If delete is overloaded, ensure that ancestor delete is called as
            well via super.


DeleteError
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.DeleteError'>,
	 <type 'exceptions.ReferenceError'>,
	 <type 'exceptions.StandardError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

InvalidPassword
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.InvalidPassword'>,
	 <class 'pride.errors.SecurityError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

InvalidSignature
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.InvalidSignature'>,
	 <class 'pride.errors.SecurityError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

InvalidTag
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.InvalidTag'>,
	 <class 'pride.errors.SecurityError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

PreprocesserError
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.PreprocesserError'>,
	 <type 'exceptions.ImportError'>,
	 <type 'exceptions.StandardError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

Proxy
--------------

	 usage: Proxy(wrapped_object=my_object) => proxied_object
    
       Produces an instance that will act as the object it wraps and as an
       Base object simultaneously. The object will act primarily as
       the wrapped object and secondly as a Proxy object. This means that       
       Proxy attributes are get/set on the underlying wrapped object first,
       and if that object does not have the attribute or it cannot be
       assigned, the action is performed on the proxy instead. This
       prioritization is the opposite of the Wrapper class.
       
       This class also supports a wrapped_object_name attribute. See 
       Base.Wrapper for more information.


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.base.Proxy'>, <class 'pride.base.Base'>, <type 'object'>)

- **wraps**(self, _object):

		 usage: wrapper.wraps(object)
            
            Makes the supplied object the object that is wrapped
            by the Proxy. 


SecurityError
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.SecurityError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

Static_Wrapper
--------------

	 Wrapper that statically wraps attributes upon initialization. This
        differs from the default Wrapper in that changes made to the data of
        the wrapped object on a Wrapper will be reflected in the wrapper object
        itself. 
        
        With a Static_Wrapper, changes made to the wrapped objects attributes 
        will not be reflected in the Static_Wrapper object, unless the object
        is explicitly wrapped again using the wraps method.
        
        Attribute access on a static wrapper is faster then the regular wrapper. 


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': (),
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.base.Static_Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **wraps**(self, _object):

				No documentation available


UnauthorizedError
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.UnauthorizedError'>,
	 <class 'pride.errors.SecurityError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

UpdateError
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.UpdateError'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

Wrapper
--------------

	 A wrapper to allow 'regular' python objects to function as a Base.
        The attributes on this wrapper will overload the attributes
        of the wrapped object. Any attributes not present on the wrapper object
        will be gotten from the underlying wrapped object. This class
        acts primarily as a wrapper and secondly as the wrapped object.
        This allows easy preemption/overloading/extension of methods by
        defining them.
        
        The class supports a "wrapped_object_name" attribute. When creating
        a new class of wrappers,  wrapped object can be made available as
        an attribute using the name given. If this attribute is not assigned,
        then the wrapped object can be accessed via the wrapped_object attribute


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': (),
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.base.Wrapper'>, <class 'pride.base.Base'>, <type 'object'>)

- **wraps**(self, _object):

		 Sets the specified object as the object wrapped by this object. 


load
--------------

**load**(saved_object):

				No documentation available


rebuild_object
--------------

**rebuild_object**(saved_data):

		 usage: load(saved_data) => restored_instance, attributes 


restore_attributes
--------------

**restore_attributes**(new_self, attributes):

		 Loads and instance from a bytestream or file produced by pride.base.Base.save. 
        Currently being reimplemented


with_metaclass
--------------

**with_metaclass**(meta, *bases):

		Create a base class with a metaclass.
