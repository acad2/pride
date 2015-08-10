mpre.authentication
==============



Authenticated_Client
--------------

	No docstring found


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
	 'protocol_client': 'mpre.srp.SRP_Client',
	 'replace_reference_on_load': True,
	 'target_service': '',
	 'username': ''}

Method resolution order: 

	(<class 'mpre.authentication.Authenticated_Client'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **login_result**(self, response):

		 Calls on_login in the event of login success, provides
            an alert upon login failure. 


- **send_proof**(self, response):

		 The second stage of the login process. This is the callback
            used by login. 


- **on_login**(self, message):

		 Called automatically upon successful login. Should be
            extended by subclasses. 


- **register_results**(self, success):

		 The callback used by the register method. Proceeds to login
            upon successful registration if auto_login is True or
            an affirmative is provided by the user. 


- **register**(self):

		 Attempt to register username with target_service operating 
            on the machine specified by host_info. A password prompt
            will be presented if password was not passed in as an 
            attribute of the authenticated_client (recommended). 


- **login**(self):

		 Attempt to log in to the target_service operating on the
            machine specified by host_info. A password prompt will be
            presented if password was not specified as an attribute of
            the authenticated_client (recommended). 


Authenticated_Service
--------------

	 Provides functionality for user registration and login, and
        provides interface for use with blacklisted/whitelisted/authenticated
        decorators. Currently uses the secure remote password protocol
        for authentication. 
        
        Note that authentication is not automatically required for all
        method calls on an Authenticated_Service object. Each method must
        be decorated explicitly with the access controls desired.


Instance defaults: 

	{'_deleted': False,
	 'allow_registration': True,
	 'database_name': '',
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'login_message': '',
	 'protocol_component': 'Secure_Remote_Password',
	 'replace_reference_on_load': True,
	 'requester_address': None}

Method resolution order: 

	(<class 'mpre.authentication.Authenticated_Service'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_load**(self, attributes):

				No documentation available


- **register**(self, username, password):

		 Register a username and corresponding password. The
            authenticated_service.allow_registration flag must be True or
            registration will fail. If the username is already registered,
            registration will fail. Returns True on successful registration. 


- **login**(self, username, credentials):

		 Attempt to log in as username using credentials. Due to
            implementation details it is best to call this method only
            via Authenticated_Client.login. 
            
            On login failure, provides non specific information as to why.
            Nonexistant username login proceeds with a fake verifier to
            defy timing attacks.

            On login success, a login message and proof of the shared
            secret are returned.


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


UnauthorizedError
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.authentication.UnauthorizedError'>,
	 <type 'exceptions.Warning'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

authenticated
--------------

**authenticated**(function):

		 Decorator to support authentication requirements for method access.
        The address of the current rpc requester is checked for membership
        in the method owners logged_in attribute. If the requester ip is
        not logged_in, the call will not be performed. 
        
        Note that the implementation may change to something non ip based. 


blacklisted
--------------

**blacklisted**(function):

		 Decorates a method to support an ip based blacklist. The address
        of the current rpc requester is checked for membership in the method
        owners blacklist attribute. If the requester ip is in the blacklist, 
        the call will not be performed. 


whitelisted
--------------

**whitelisted**(function):

		 Decorator to support an ip based whitelist. The address of the
        current rpc requester is checked for membership in the method
        owners whitelist attribute. If the requesters ip is not in the
        whitelist, the call will not be performed. 
