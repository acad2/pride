mpre.base
========
No documentation available

Base
--------
	 usage: instance = Base(attribute=value, ...)
	
	The root inheritance object that provides many of the features
	of the runtime environment. An object that inherits from base will 
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
	  of varying verbosity simple and straight forward. Alerts
	  also include options for callback methods and instructions
	  
	- The method known as parallel_method. This method is used in a 
	  similar capacity to Instruction objects, but the
	  call happens immediately and the return value from the
	  specified method is available
	  
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
	mpre.environment.Component_Resolve. The instance_name is used
	for lookups in Instructions, parallel method calls, and reactions.
	
	Base objects can specify a memory_size attribute. If specified,
	the object will have a .memory attribute. This is a chunk of
	anonymous, contiguous memory of the size specified, provided
	by pythons mmap.mmap. This memory attribute can be useful because 
	it supports both the file-style read/write/seek interface and 
	string-style slicing

Default values for newly created instances:

- deleted                  False
- verbosity                
- memory_size              4096
- memory_mode              -1
- update_flag              False

This object defines the following non-private methods:


- **set_attributes**(self, **kwargs):

		  usage: object.set_attributes(attr1=value1, attr2=value2).
		 
		 Each key:value pair specified as keyword arguments will be
		 assigned as attributes of the calling object. Keys are string
		 attribute names and the corresponding values can be anything.
		 
		 This is called implicitly in __init__ for Base objects.



- **update**(self):

		  usage: base.update() => updated_base
		 
		 Reloads the module that defines base and returns an updated instance. 
		 The environment is updated with the new component information. Further
		 references to the object via instance_name will be directed to the
		 new, updated object. Attributes of the original object will be assigned
		 to the new, updated object.
		 
		 This is the bleeding edge. not solid in terms of object deletion yet.



- **alert**(self, message='Unspecified alert message', format_args=(), level=0, callback=None):

		  usage: base.alert(message, format_args=tuple(), level=0, callback=None)
		 
		 Create an alert. Depending on the level given, the alert may be printed
		 for immediate attention and/or logged quietly for later viewing.
		 
		 -message is a string that will be logged and/or displayed
		 -format_args are any string formatting args for message.format()
		 -level is an integer indicating the severity of the alert.
		 -callback is an optional tuple of (function, args, kwargs) to be called when
		  the alert is triggered
		 
		 alert severity is relative to Alert_Handler log_level and print_level;
		 a lower number indicates a less verbose notification, while 0 indicates
		 an important message that should not be suppressed.



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
		 need for an explicit reference to that object.



- **create**(self, instance_type, *args, **kwargs):

		  usage: object.create("module_name.object_name", 
		                     args, kwargs) => instance
		 
		 Given a type or string reference to a type, and arguments,
		 return an instance of the specified type. The creating
		 object will call .add on the created object, which
		 performs reference tracking maintainence.



- **remove**(self, instance):

		  Usage: object.remove(instance)
		 
		 Removes an instance from self.objects. Modifies object.objects
		 and environment.References_To



- **add**(self, instance):

		  usage: object.add(instance)
		 
		 Adds an object to caller.objects[instance.__class__.__name__]



- **delete**(self):

		  usage: object.delete()
		 
		 Explicitly delete a component. This calls remove and
		 attempts to clear out known references to the object so that
		 the object can be collected by the python garbage collector


This objects method resolution order is:

(class 'mpre.base.Base', type 'object')


Proxy
--------
	 usage: Proxy(wrapped_object=my_object) => proxied_object
	
	   Produces an instance that will act as the object it wraps and as an
	   Reactor object simultaneously. This facilitates simple integration 
	   with 'regular' python objects, providing them with monkey patches and
	   the reaction/parallel_method/alert interfaces for very little effort.
	   
	   Proxy attributes are get/set on the underlying wrapped object first,
	   and if that object does not have the attribute or it cannot be
	   assigned, the action is performed on the proxy wrapper instead.

Default values for newly created instances:

- deleted                  False
- verbosity                
- memory_size              4096
- memory_mode              -1
- update_flag              False

This object defines the following non-private methods:


- **wraps**(self, obj, set_defaults=False):

		  usage: wrapper.wraps(object)
		 
		 Makes the supplied object the object that is wrapped
		 by the calling wrapper. If the optional set_defaults
		 attribute is True, then the wrapped objects class
		 defaults will be applied.


This objects method resolution order is:

(class 'mpre.base.Proxy', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Reactor
--------
	 usage: Reactor(attribute=value, ...) => reactor_instance
	
	Adds reaction framework on top of a Base object. 
	Reactions are event triggered chains of method calls
	
	This class is a recent addition and may not be completely
	final in it's api and/or implementation.
	TODO: add transparent remote reaction support!

Default values for newly created instances:

- deleted                  False
- verbosity                
- memory_size              4096
- memory_mode              -1
- update_flag              False

This object defines the following non-private methods:


- **reaction**(self, component_name, message, _response_to='None', scope='local'):

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



- **respond_with**(self, method):

		  usage: self.respond_with(method)
		 
		 Specifies what method should be called when the component
		 specified by a reaction returns its response.



- **react**(self, sender, packet):

		  No documentation available


This objects method resolution order is:

(class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Wrapper
--------
	 A wrapper to allow python objects to function as a Reactor.
	The attributes on this wrapper will overload the attributes
	of the wrapped object. 

Default values for newly created instances:

- deleted                  False
- verbosity                
- memory_size              4096
- memory_mode              -1
- update_flag              False

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')
