mpre.authentication
==============



Authenticated
--------------

**Authenticated**(function):

				No documentation available


Authenticated_Client
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'auto_login': True,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'host_info': ('localhost', 40022),
	 'logged_in': False,
	 'password': '',
	 'password_prompt': 'Please provide the pass phrase or word: ',
	 'protocol_client': 'mpre.srp.SRP_Client',
	 'replace_reference_on_load': True,
	 'target_service': '',
	 'username': '',
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.authentication.Authenticated_Client'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **send_proof**(self, response):

				No documentation available


- **login_result**(self, response):

				No documentation available


- **register**(self):

				No documentation available


- **on_login**(self, message):

				No documentation available


- **register_results**(self, success):

				No documentation available


- **login**(self):

				No documentation available


Authenticated_Service
--------------

	 Warning: not yet secure by any means


Instance defaults: 

	{'_deleted': False,
	 'allow_registration': True,
	 'database_filename': 'user_registry',
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'login_message': '',
	 'protocol_component': 'Secure_Remote_Password',
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.authentication.Authenticated_Service'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **login**(self, username, credentials):

				No documentation available


- **register**(self, username, password):

				No documentation available


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
            
            host_info may be specified to designate a remote machine that
            the Instruction should be executed on. If host_info is supplied
            and callback is None, the results of the instruction will be 
            supplied to RPC_Handler.alert.


UnauthorizedError
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.authentication.UnauthorizedError'>,
	 <type 'exceptions.Warning'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)