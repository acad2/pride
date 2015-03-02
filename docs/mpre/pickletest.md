mpre.pickletest
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
	  for this is simply:
	  
	component.method(decorator='module.Decorator')
	component.method(decorators=['module.Decorator', ...])
	component.method(monkey_patch='module.Method')
	  
	  The usage of these does not permanently wrap/replace the
	  method. The decorator/patch is only applied when specified.
	
	- Augmented docstrings. Information about class defaults
	  and method names + argument signatures + method docstrings (if any)
	  is included automatically. 
	  
	Note that some features are facilitated by the metaclass. These include
	the argument parser, runtime decoration, and documentation.
	
	Instances of Base classes are counted and have an instance_name attribute.
	This is equal to type(instance).__name__ + str(instance_count). There
	is an exception to this; The first instance is instance # 0 and
	it's name is simply type(instance).__name__, without 0 at the end.
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

		  usage: object.create("module_name.object_name", args, kwargs)
		 
		 The specified python object will be instantiated with the given arguments
		 and placed inside object.objects under the created objects class name via
		 the add method



- **remove**(self, instance):

		  Usage: object.remove(instance)
		 
		 Removes an instance from self.objects



- **add**(self, instance):

		  usage: object.add(instance)
		 
		 adds an instance to the instances' class name entry in parent.objects.



- **delete**(self):

		  usage: object.delete() or object.delete(child). thoroughly untested.


This objects method resolution order is:

(class 'mpre.base.Base', type 'object')


Instruction
--------
 usage: Instruction(component_name, method_name, 
                           *args, **kwargs) => instruction_object
                           
        Creates an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        Instruction objects have a priority attribute. This attribute
        defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds. 
        
        Instructions may be saved as an attribute of a component instead
        of continuously being instantiated. This allows the reuse of
        instruction objects. 
        
        Note that Instructions must be executed to have any effect, and
        that they do not happen inline, even if priority is 0.0. 
        Because they do not execute in the current scope, the return value 
        from the method call is not available through this mechanism.

Interpreter_Service
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- database_filename        :memory:
- memory_size              4096
- copyright                Type "help", "copyright", "credits" or "license" for more information.
- deleted                  False
- verbosity                
- login_message            login success

This object defines the following non-private methods:


- **exec_code**(instance, sender, packet):

		  No documentation available



- **login**(self, sender, packet):

		  No documentation available


This objects method resolution order is:

(class 'mpre.metapython.Interpreter_Service', class 'mpre.network2.Authenticated_Service', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Metapython
--------
	No docstring found

Default values for newly created instances:

- prompt                   >>> 
- deleted                  False
- startup_definitions      Instruction('Metapython', 'create', 'userinput.User_Input').execute()
Instruction("Metapython", "create", "network.Asynchronous_Network").execute()
- memory_size              4096
- interface                0.0.0.0
- port                     40022
- _suspended_file_name     suspended_interpreter.bin
- network_packet_size      4096
- interpreter_enabled      True
- copyright                Type "help", "copyright", "credits" or "license" for more information.
- implementation           python
- verbosity                
- environment_setup        ['PYSDL2_DLL_PATH = C:\\Python27\\DLLs']
- priority                 0.04
- command                  shell_launcher.py
- auto_start               True

This object defines the following non-private methods:


- **start_service**(self):

		  No documentation available



- **start_machine**(self):

		  No documentation available



- **save_state**(self):

		  No documentation available



- **exit**(self, exit_code=0):

		  No documentation available



- **load_state**(pickle_filename):

		  No documentation available



- **exec_command**(self, source):

		  No documentation available



- **setup_os_environ**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.metapython.Metapython', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Shell
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- username                 root
- prompt                   >>> 
- target                   Interpreter_Service
- deleted                  False
- verbosity                
- startup_definitions      
- memory_size              4096
- password                 password
- email                    

This object defines the following non-private methods:


- **login_result**(self, sender, packet):

		  No documentation available



- **exec_code_request**(self, sender, source):

		  No documentation available



- **result**(self, sender, packet):

		  No documentation available



- **execute_source**(self, source):

		  No documentation available



- **handle_keystrokes**(self, sender, keyboard_input):

		  No documentation available


This objects method resolution order is:

(class 'mpre.metapython.Shell', class 'mpre.network2.Authenticated_Client', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Timed
--------
No documentation available