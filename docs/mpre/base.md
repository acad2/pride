mpre.base
========
No documentation available

Alert
--------
No documentation available

Base
--------
	A base object to inherit from. An object that inherits from base
	can have arbitrary attributes set upon object instantiation by specifying
	them as keyword arguments. An object that inherits from base will also
	be able to create/hold arbitrary python objects by specifying them as
	arguments to create. Classes that inherit from base should specify a class.defaults 
	dictionary that will automatically include the specified (attribute, value) pairs on 
	all new instances.

Default values for newly created instances:

- network_packet_size      4096
- deleted                  False
- verbosity                
- memory_size              4096

This object defines the following non-private methods:


- **read_messages**(self):

		  No documentation available



- **get_family_tree**(self):

		  usage: all_objects = object.get_family_tree()
		 
		 returns a dictionary containing all the children/descendants of object



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
		 an error or exception and will never be suppressed.



- **remove**(self, instance):

		  No documentation available



- **public_method**(self, component_name, method_name, *args, **kwargs):

		  usage: base.public_method(component_name, method_name, *args, **kwargs) =>
		        component.method(*args, **kwargs)
		        
		 Used to call the method of an external object directly without using 
		 instructions or message sending/reading. Public methods are designated in
		 the public_methods field of a class object. Attempting to call a
		 public_method on an object that does not specify the method as public
		 will result in a ValueError. This call is not scheduled by the processor
		 and happens immediately. The return value from the external method is 
		 returned by this call.



- **create**(self, instance_type, *args, **kwargs):

		  usage: object.create("module_name.object_name", args, kwargs)
		 
		 The specified python object will be instantiated with the given arguments
		 and placed inside object.objects under the created objects class name via
		 the add method



- **send_to**(self, component_name, message):

		  No documentation available



- **get_children**(self):

		  usage: for child in object.get_children...
		 
		 Creates a generator that yields the immediate children of the object.
		 WARNING: do not mutate self.objects when using this



- **add**(self, instance):

		  usage: object.add(other_object)
		 
		 adds an already existing object to the instances' class name entry in parent.objects.



- **delete**(self):

		  usage: object.delete() or object.delete(child). thoroughly untested.


This objects method resolution order is:

(class 'mpre.base.Base', type 'object')


Docstring
--------
No documentation available

Documented
--------
No documentation available

Instruction
--------
No documentation available

Metaclass
--------
Includes class.defaults attribute/values in docstrings.
Applies the Runtime_Decorator to class methods.
Adds instance trackers to classes.

Parser
--------
	No docstring found




This object defines the following non-private methods:


- **get_options**(self, argument_info):

		  No documentation available



- **get_arguments**(self, argument_info):

		  No documentation available


This objects method resolution order is:

(class 'mpre.base.Parser', type 'object')


Runtime_Decorator
--------
	provides the ability to call a function with a decorator specified via
	keyword argument.
	
	example: my_function(my_argument1, decorator="decoratorlibary.Tracer")




No non-private methods are defined

This objects method resolution order is:

(class 'mpre.base.Runtime_Decorator', type 'object')


Wrapper
--------
	a class that will act as the object it wraps and as a base
	object simultaneously.

Default values for newly created instances:

- network_packet_size      4096
- deleted                  False
- verbosity                
- memory_size              4096

This object defines the following non-private methods:


- **wraps**(self, obj, set_defaults=False):

		  No documentation available


This objects method resolution order is:

(class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')
