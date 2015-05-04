mpre._metapython
==============



Alert_Handler
--------------

	 Provides the backend for the base.alert method. This component is automatically
        created by the Metapython component. The print_level and log_level attributes act
        as global filters for alerts; print_level and log_level may be specified as 
        command line arguments upon program startup to globally control verbosity/logging.


Instance defaults: 

	{'_deleted': False,
	 'log_level': 0,
	 'log_name': 'Alerts.log',
	 'print_level': 0,
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre._metapython.Alert_Handler'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Instruction
--------------

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
        that they do not happen inline even if the priority is 0.0. In
        order to access the result of the executed function, a callback
        function can be provided.


Method resolution order: 

	(<class 'mpre.Instruction'>, <type 'object'>)

- **execute**(self, priority, callback, host_info, transport_protocol):

		 usage: instruction.execute(priority=0.0, callback=None)
        
            Submits an instruction to the processing queue. The instruction
            will be executed in priority seconds. An optional callback function 
            can be provided if the return value of the instruction is needed.


Interpreter_Service
--------------

	 Provides the server side of the interactive interpreter. Receives keystrokes
        and attempts to compile + exec them.


Instance defaults: 

	{'_deleted': False,
	 'copyright': 'Type "help", "copyright", "credits" or "license" for more information.',
	 'database_filename': ':memory:',
	 'hash_rounds': 100000,
	 'login_message': 'login success',
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre._metapython.Interpreter_Service'>,
	 <class 'mpre.network2.Authenticated_Service'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **call**(instance, sender, packet):

		No documentation available


- **login**(self, sender, packet):

		No documentation available


Metapython
--------------

	 Provides an entry point to the environment. Instantiating this component and
        calling the start_machine method starts the execution of the Processor component.
        It is encouraged to use the Metapython component when create-ing new top level
        components in the environment. For example, the Network component is a child object
        of the Metapython component. Doing so allows for simple portability of an environment
        in regards to saving/loading the state of an entire application.


Instance defaults: 

	{'_deleted': False,
	 'command': 'c:\\users\\_\\pythonbs\\mpre\\shell_launcher.py',
	 'copyright': 'Type "help", "copyright", "credits" or "license" for more information.',
	 'environment_setup': ['PYSDL2_DLL_PATH = C:\\Python27\\DLLs'],
	 'implementation': 'python',
	 'interface': '0.0.0.0',
	 'interpreter_enabled': True,
	 'port': 40022,
	 'prompt': '>>> ',
	 'replace_reference_on_load': True,
	 'startup_components': ('mpre.fileio.File_System',
	                        'vmlibrary.Processor',
	                        'mpre._metapython.Alert_Handler',
	                        'mpre.userinput.User_Input',
	                        'mpre.network.Network',
	                        'mpre.network2.RPC_Handler'),
	 'startup_definitions': '',
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre._metapython.Metapython'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **main_as_name**(, *args, **kwds):

		No documentation available


- **start_machine**(self):

		 Begins the processing of Instruction objects.


- **exec_command**(self, source):

		 Executes the supplied source as the __main__ module


- **start_service**(self):

		No documentation available


- **exit**(self, exit_code):

		No documentation available


- **setup_os_environ**(self):

		 This method is called automatically in Metapython.__init__; os.environ can
            be customized on startup via modifying Metapython.defaults["environment_setup"].
            This can be useful for modifying system path only for the duration of the applications run time.


Shell
--------------

	 Provides the client side of the interpreter session. Handles keystrokes and
        sends them to the Interpreter_Service to be executed.


Instance defaults: 

	{'_deleted': False,
	 'email': '',
	 'password': 'password',
	 'prompt': '>>> ',
	 'replace_reference_on_load': True,
	 'startup_definitions': '',
	 'target': 'Interpreter_Service',
	 'username': 'root',
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre._metapython.Shell'>,
	 <class 'mpre.network2.Authenticated_Client'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

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
