mpre.base
==============

 Contains The root inheritance objects that provides many of the features
    of the runtime environment. An object that inherits from mpre.base.Base will 
    possess these capabilities:
        
        - When instantiating, arbitrary attributes may be assigned
          via keyword arguments
          
        - The class includes a defaults attribute, which is a dictionary
          of name:value pairs. These pairs will be assigned as attributes
          to new instances; Any attribute specified via keyword argument
          will override a default
          
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
          
        - parallel_method calls. This is the primary concurreny mechanism 
          and is used in a similar capacity to Instruction objects.
          The difference is that the call happens immediately and the return 
          value from the specified method is available in the calling scope
          
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
          is included automatically. 
          
    Note that some features are facilitated by the metaclass. These include
    the argument parser, runtime decoration, and documentation.
    
    Instances of Base classes are counted and have an instance_name attribute.
    This is equal to type(instance).__name__ + str(instance_count). There
    is an exception to this; The first instance is number 0 and
    its name is simply type(instance).__name__, without 0 at the end.
    This name associates the instance to the instance_name in the
    mpre.environment.Component_Resolve. The instance_name can be used to reference
    the object from any scope, as long as the component exists.

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

	{'_deleted': False, 'replace_reference_on_load': True, 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.base.Base'>, <type 'object'>)

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


- **parallel_method**(self, component_name, method_name, *args, **kwargs):

		 usage: base.parallel_method(component_name, method_name, 
                                       *args, **kwargs) 
                                       => component.method(*args, **kwargs)
                  
            Used to call the method of an existing external component.
           
            -component_name is a string of the instance_name of the component
            -method_name is a string of the method to be called
            -arguments and keyword arguments for the method may optionally
             be supplied after the component_name and method_name
             
            The method is called immediately and the return value of the
            method is made available as the return value of parallel_method.
            
            parallel_method allows for the use of an object without the
            need for a reference to that object in the current scope.


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
            and environment.References_To.


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
       Reactor object simultaneously. The object will act primarily as
       the wrapped object and secondly as a proxy object. This means that       
       Proxy attributes are get/set on the underlying wrapped object first,
       and if that object does not have the attribute or it cannot be
       assigned, the action is performed on the proxy instead. This
       prioritization is the opposite of the Wrapper class.


Instance defaults: 

	{'_deleted': False, 'replace_reference_on_load': True, 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.base.Proxy'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **wraps**(self, obj, set_defaults):

		 usage: wrapper.wraps(object)
            
            Makes the supplied object the object that is wrapped
            by the calling wrapper. If the optional set_defaults
            attribute is True, then the wrapped objects class
            defaults will be applied.


Reactor
--------------

	 usage: Reactor(attribute=value, ...) => reactor_instance
    
        Adds reaction framework on top of a Base object. 
        Reactions are event triggered chains of method calls
        
        This class is a recent addition and is far from final in it's api and
        implementation. 


Instance defaults: 

	{'_deleted': False, 'replace_reference_on_load': True, 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.base.Reactor'>, <class 'mpre.base.Base'>, <type 'object'>)

- **reaction**(self, component_name, message, _response_to, scope):

		Usage: component.reaction(target_component, message, 
                                    [scope='local'])
        
            calls a method on target_component. message is a string that
            contains the method name followed by arguments separate by
            spaces. 
            
            The scope keyword specifies the location of the expected
            component, and the way the component will be reached.
            
            When scope is 'local', the component is the component that resides
            under the specified name in environment.Component_Resolve. This
            reaction happens immediately.
            
            The following is not implemented as of 3/1/2015:
            When scope is 'global', the component is a parallel reactor
            and the message will be written to memory. This reaction is
            scheduled among worker processes.
            
            When scope is "network", the component is a remote reactor
            on a remote machine and the message will be sent via a reaction 
            with the service proxy, which sends the request via the network.
            
            If scope is 'network', then component_name is a tuple containing
            the component name and a tuple containing the host address port


- **respond_with**(self, method_name):

		 usage: self.respond_with(method)
        
            Specifies what method should be called when the component
            specified by a reaction returns its response.


- **react**(self, sender, packet):

		No documentation available


UpdateError
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.errors.UpdateError'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

Wrapper
--------------

	 A wrapper to allow 'regular' python objects to function as a Reactor.
        The attributes on this wrapper will overload the attributes
        of the wrapped object. Any attributes not present on the wrapper object
        will be gotten from the underlying wrapped object. This class
        acts primarily as a wrapper and secondly as the wrapped object.


Instance defaults: 

	{'_deleted': False, 'replace_reference_on_load': True, 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **wraps**(self, _object):

		No documentation available
