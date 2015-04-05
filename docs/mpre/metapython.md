mpre.metapython
========
No documentation available

Alert_Handler
--------
	No docstring found

Default values for newly created instances:

- log_name                 Alerts.log
- memory_mode              -1
- deleted                  False
- verbosity                
- print_level              0
- memory_size              4096
- update_flag              False
- log_level                0

This object defines the following non-private methods:


- **alert**(self, message, level, callback):

		  No documentation available


This objects method resolution order is:

(class 'mpre.metapython.Alert_Handler', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


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

Interpreter_Service
--------
	No docstring found

Default values for newly created instances:

- database_filename        :memory:
- copyright                Type "help", "copyright", "credits" or "license" for more information.
- memory_mode              -1
- deleted                  False
- verbosity                
- memory_size              4096
- update_flag              False
- login_message            login success
- hash_rounds              100000

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
- memory_mode              -1
- deleted                  False
- startup_definitions      Instruction('Metapython', 'create', 'userinput.User_Input').execute()
Instruction("Metapython", "create", "network.Network").execute()
- memory_size              4096
- interface                0.0.0.0
- port                     40022
- _suspended_file_name     suspended_interpreter.bin
- interpreter_enabled      True
- copyright                Type "help", "copyright", "credits" or "license" for more information.
- implementation           python
- verbosity                
- environment_setup        ['PYSDL2_DLL_PATH = C:\\Python27\\DLLs']
- priority                 0.04
- command                  shell_launcher.py
- update_flag              False

This object defines the following non-private methods:


- **start_machine**(self):

		  No documentation available



- **load_state**(pickle_filename):

		  usage: from metapython import *
		         Metapython.load_state(pickle_filename) => interpreter
		         
		 Load an environment that was saved by Metapython.save_state.
		 The package global mpre.environment is updated with the
		 contents of the restored environment, and the component at
		 environment.Component_Resolve["Metapython"] is returned by this
		 method.



- **exec_command**(self, source):

		  No documentation available



- **start_service**(self):

		  No documentation available



- **save_state**(self):

		  usage: metapython.save_state()
		 
		 Stores a snapshot of the current runtime environment. 
		 This file is saved as metapython._suspended_file_name, which
		 defaults to "suspended_interpreter.bin".



- **exit**(self, exit_code=0):

		  No documentation available



- **setup_os_environ**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.metapython.Metapython', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Restored_Interpreter
--------
	 usage: Restored_Intepreter(filename="suspended_interpreter.bin") => interpreter
	
	Restores an interpreter environment that has been suspended via
	metapython.Metapython.save_state. This is a convenience class
	over Metapython.load_state; instances produced by instantiating
	Restored_Interpreter will be of the type of instance returned by
	Metapython.load_state and not Restored_Interpreter

Default values for newly created instances:

- prompt                   >>> 
- memory_mode              -1
- deleted                  False
- startup_definitions      Instruction('Metapython', 'create', 'userinput.User_Input').execute()
Instruction("Metapython", "create", "network.Network").execute()
- memory_size              4096
- interface                0.0.0.0
- port                     40022
- _suspended_file_name     suspended_interpreter.bin
- interpreter_enabled      True
- copyright                Type "help", "copyright", "credits" or "license" for more information.
- implementation           python
- verbosity                
- environment_setup        ['PYSDL2_DLL_PATH = C:\\Python27\\DLLs']
- filename                 suspended_interpreter.bin
- priority                 0.04
- command                  shell_launcher.py
- update_flag              False

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.metapython.Restored_Interpreter', class 'mpre.metapython.Metapython', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Shell
--------
	No docstring found

Default values for newly created instances:

- username                 root
- prompt                   >>> 
- target                   Interpreter_Service
- memory_mode              -1
- deleted                  False
- verbosity                
- startup_definitions      
- memory_size              4096
- update_flag              False
- password                 password
- email                    

This object defines the following non-private methods:


- **handle_startup_definitions**(self):

		  No documentation available



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
