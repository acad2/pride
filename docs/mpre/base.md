mpre.base
========
No documentation available

Alert
--------
 Utilizes a class as a namespace for holding global alert related
        configuration. This class is not instantiated anywhere.
        
        Contains the log_level and print_level global settings for alerts.
        The actual log file is Alert.log, which defaults to Alerts.log.
        The level_map associates alert level symbols with notification level

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
	by pythons mmap.mmap. The memory attribute can be useful because 
	it supports both the file-style read/write/seek interface and 
	string-style slicing

Default values for newly created instances:

- network_packet_size      4096
- deleted                  False
- verbosity                
- memory_size              4096

This object defines the following non-private methods:


- **attribute_setter**(self, **kwargs):

		  usage: object.attribute_setter(attr1=value1, attr2=value2).
		 called implicitly in __init__ for any object that inherits from Base.



- **alert**(self, message='Unspecified alert message', format_args=(), level=0, callback=None, callback_instruction=None):

		  usage: base.alert(message, format_args, level, callback, callback_instruction)
		 
		 Create an alert. Depending on the level given, the alert may be printed
		 for immediate attention and/or logged quietly for later viewing.
		 
		 -message is a string that will be logged and/or displayed
		 -format_args are any string formatting args for message.format()
		 -level is a small integer indicating the severity of the alert.
		 -callback is an optional tuple of (function, args, kwargs) to be called when
		 the alert is triggered
		 -callback_instruction is an optional Instruction to be posted when the alert is triggered.
		 
		 alert severity is relative to the Alert.log_level and Alert.print_level;
		 a lower number indicates a less verbose notification, while 0 indicates
		 an important message that should not and will never be suppressed.



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
		 
		 Adds an object to the calling object. This performs
		 reference bookkeeping so the added object can be 
		 deleted successfully later.



- **delete**(self):

		  usage: object.delete()
		 
		 Explicitly delete a component. This calls remove and
		 attempts to clear out known references to the object so that
		 the object can be garbage collected by the regular python collector


This objects method resolution order is:

(class 'mpre.base.Base', type 'object')


Instruction
--------
 usage: Instruction(component_name, method_name, 
                           *args, **kwargs).execute(priority=priority)
                           
        Creates and executes an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds. 
        
        Instructions may be saved as an attribute of a component instead
        of continuously being instantiated. This allows the reuse of
        instruction objects. The same instruction object can be executed 
        any number of times.
        
        Note that Instructions must be executed to have any effect, and
        that they do not happen inline, even if priority is 0.0. 
        Because they do not execute in the current scope, the return value 
        from the method call is not available through this mechanism.

Reactor
--------
	 usage: instance = Reactor(attribute=value, ...)
	
	Adds reaction framework on top of a Base object. 
	Reactions are event triggered chains of method calls
	
	This class is a recent addition and may not be completely
	final in it's api and/or implementation.
	TODO: add transparent remote reaction support!

Default values for newly created instances:

- network_packet_size      4096
- deleted                  False
- verbosity                
- memory_size              4096

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
	 usage: Wrapper(wrapped_object=my_object) => wrapped_object
	
	   Produces an instance that will act as the object it wraps and as an
	   Reactor object simultaneously. This facilitates simple integration 
	   with 'regular' python objects, providing them with monkey patches and
	   the reaction/parallel_method/alert interfaces for very little effort.

Default values for newly created instances:

- network_packet_size      4096
- deleted                  False
- verbosity                
- memory_size              4096

This object defines the following non-private methods:


- **wraps**(self, obj, set_defaults=False):

		  usage: wrapper.wraps(object)
		 
		 Makes the supplied object the object that is wrapped
		 by the calling wrapper. If the optional set_defaults
		 attribute is True, then the wrapped objects class
		 defaults will be applied.


This objects method resolution order is:

(class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')
