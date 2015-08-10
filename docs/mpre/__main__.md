__main__
==============

 Builds the metapython runtime environment package 

Instruction
--------------

	 usage: Instruction(component_name, method_name, 
                           *args, **kwargs).execute(priority=priority,
                                                    callback=callback,
                                                    host_info=(ip, port))
                           
        Creates and executes an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        host_info may supply an ip address string and port number integer
        to execute the instruction on a remote machine. This requirements
        for this to be a success are:
            
            - The machine must have an instance of metapython running
            - The machine must be accessible via the network
            - The local machine must be registered and logged in to
              the remote machine
            - The local machine may need to be registered and logged in to
              have permission to the use the specific component and method
              in question
            - The local machine ip must not be blacklisted by the remote
              machine.
            - The remote machine may require that the local machine ip
              be in a whitelist to access the method in question.
              
        Other then the security requirements, remote procedure calls require 
        zero config on the part of either host. An object will be accessible
        if it exists on the machine in question.
              
        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed if the instruction is being executed
        locally. If the instruction is being executed remotely, this instead
        acts as a flag. If set to a True value, the instruction will be
        placed at the front of the local queue to be sent to the host.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds or sent to the machine in question. 
        
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

		 usage: instruction.execute(priority=0.0, callback=None,
                                       host_info=tuple())
        
            Submits an instruction to the processing queue. If being executed
            locally, the instruction will be executed in priority seconds. 
            An optional callback function can be provided if the return value 
            of the instruction is needed.
            
            host_info may be specified to designate a remote machine that
            the Instruction should be executed on. If being executed remotely, 
            priority is a high_priority flag where 0 means the instruction will
            be placed at the end of the rpc queue for the remote host in 
            question. If set, the instruction will instead be placed at the 
            beginning of the queue.
            
            Remotely executed instructions have a default callback, which is 
            the appropriate RPC_Requester.alert.
            
            The transport protocol flag is currently unused. Support for
            UDP and other protocols could be implemented and dispatched
            via this flag.


Interpreter
--------------

	 Executes python source. Requires authentication. The source code and 
        return value of all requests are logged.
        
        usage: Instruction("Interpreter", "exec_code",
                           my_source).execute(host_info=target_host)


Instance defaults: 

	{'_deleted': False,
	 'allow_registration': True,
	 'copyright': 'Type "help", "copyright", "credits" or "license" for more information.',
	 'database_name': '',
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'login_message': '',
	 'protocol_component': 'Secure_Remote_Password',
	 'replace_reference_on_load': True,
	 'requester_address': None}

Method resolution order: 

	(<class 'mpre._metapython.Interpreter'>,
	 <class 'mpre.authentication.Authenticated_Service'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **call**(instance, *args, **kwargs):

				No documentation available


- **login**(self, username, credentials):

				No documentation available


Metapython
--------------

	 The "main" class. Provides an entry point to the environment. 
        Instantiating this component and calling the start_machine method 
        starts the execution of the Processor component.


Instance defaults: 

	{'_deleted': False,
	 'command': 'c:\\users\\_\\pythonbs\\mpre\\shell_launcher.py',
	 'copyright': 'Type "help", "copyright", "credits" or "license" for more information.',
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'environment_setup': ['PYSDL2_DLL_PATH = C:\\Python27\\DLLs'],
	 'interpreter_enabled': True,
	 'prompt': '>>> ',
	 'replace_reference_on_load': True,
	 'startup_components': ('mpre.vmlibrary.Processor',
	                        'mpre.network.Socket_Error_Handler',
	                        'mpre.network.Network',
	                        'mpre.shell.Command_Line',
	                        'mpre.srp.Secure_Remote_Password',
	                        'mpre.rpc.RPC_Handler'),
	 'startup_definitions': ''}

Method resolution order: 

	(<class 'mpre._metapython.Metapython'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **main_as_name**(, *args, **kwds):

				No documentation available


- **start_machine**(self):

		 Begins the processing of Instruction objects.


- **enable_interpreter**(self):

				No documentation available


- **exit**(self, exit_code):

				No documentation available


- **exec_command**(self, source):

		 Executes the supplied source as the __main__ module


- **setup_os_environ**(self):

		 This method is called automatically in Metapython.__init__; os.environ can
            be customized on startup via modifying Metapython.defaults["environment_setup"].
            This can be useful for modifying system path only for the duration of the applications run time.


Shell
--------------

	 Handles keystrokes and sends python source to the Interpreter to 
        be executed. This requires authentication via username/password.


Instance defaults: 

	{'_deleted': False,
	 'auto_login': True,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'ip': 'localhost',
	 'logged_in': False,
	 'password': '',
	 'password_prompt': '{}: Please provide the pass phrase or word: ',
	 'port': 40022,
	 'prompt': '>>> ',
	 'protocol_client': 'mpre.srp.SRP_Client',
	 'replace_reference_on_load': True,
	 'startup_definitions': '',
	 'target_service': 'Interpreter',
	 'username': ''}

Method resolution order: 

	(<class 'mpre._metapython.Shell'>,
	 <class 'mpre.authentication.Authenticated_Client'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **handle_startup_definitions**(self):

				No documentation available


- **execute_source**(self, source):

				No documentation available


- **result**(self, packet):

				No documentation available


- **handle_input**(self, input):

				No documentation available


- **on_login**(self, message):

				No documentation available


Version_Manager
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'author': '',
	 'author_email': '',
	 'delete_verbosity': 'vv',
	 'description': '',
	 'dont_save': False,
	 'name': '',
	 'options': ('name',
	             'version',
	             'description',
	             'url',
	             'author',
	             'author_email',
	             'packages'),
	 'packages': '',
	 'replace_reference_on_load': True,
	 'setuppy_directory': '..',
	 'url': '',
	 'version': ''}

Method resolution order: 

	(<class '__main__.Version_Manager'>, <class 'mpre.base.Base'>, <type 'object'>)

- **increment_version**(self, amount):

				No documentation available


- **run_setup**(self, argv):

				No documentation available
