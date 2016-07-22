pride.authentication2
==============



Authenticated_Client
--------------

	No docstring found


Instance defaults: 

	{'_register_results': None,
	 '_user_database': '',
	 'authentication_table_size': 256,
	 'auto_login': True,
	 'challenge_size': 9,
	 'deleted': False,
	 'dont_save': False,
	 'hash_function': 'SHA256',
	 'hkdf_table_update_info_string': 'Authentication Table Update',
	 'ip': 'localhost',
	 'parse_args': False,
	 'password_prompt': '{}: Please provide the pass phrase or word for {}@{}: ',
	 'port': 40022,
	 'replace_reference_on_load': True,
	 'shared_key_size': 32,
	 'startup_components': (),
	 'target_service': '/Python/Authenticated_Service',
	 'token_file_encrypted': True,
	 'token_file_indexable': False,
	 'token_file_type': 'pride.fileio.Database_File',
	 'username_prompt': '{}: Please provide the user name for {}@{}: '}

Method resolution order: 

	(<class 'pride.authentication2.Authenticated_Client'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **handle_login_failure**(self):

				No documentation available


- **on_login**(self, login_message):

				No documentation available


- **new_call**(args, **kwargs):

				No documentation available


- **decrypt_new_secret**(self, encrypted_key):

				No documentation available


- **new_call**(self, *args, **kwargs):

				No documentation available


- **on_load**(self, attributes):

				No documentation available


- **new_call**(args, **kwargs):

				No documentation available


- **handle_not_logged_in**(self, instruction, callback):

				No documentation available


- **new_call**(args, **kwargs):

				No documentation available


- **delete**(self):

				No documentation available


Authenticated_Service
--------------

	No docstring found


Instance defaults: 

	{'allow_login': True,
	 'allow_registration': True,
	 'authentication_table_size': 256,
	 'challenge_size': 9,
	 'database_name': '',
	 'database_type': 'pride.database.Database',
	 'deleted': False,
	 'dont_save': False,
	 'hash_function': 'SHA256',
	 'hkdf_table_update_info_string': 'Authentication Table Update',
	 'login_message': 'Welcome to the {}, {} from {}',
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'shared_key_size': 32,
	 'startup_components': (),
	 'validation_failure_string': ".validate: Authorization Failure:\n    ip blacklisted: {}    ip whitelisted: {}\n    session_id logged in: {}\n    method_name: '{}'    method available remotely: {}\n    login allowed: {}    registration allowed: {}"}

Method resolution order: 

	(<class 'pride.authentication2.Authenticated_Service'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **execute_remote_procedure_call**(self, session_id, peername, method_name, args, kwargs):

				No documentation available


- **logout**(self):

				No documentation available


- **validate**(self, session_id, peername, method_name):

		 Determines whether or not the peer with the supplied
            session id is allowed to call the requested method.

            Sets current_session attribute to (session_id, peername) if validation
            is successful. 


- **on_load**(self, attributes):

				No documentation available


- **register**(self, username):

				No documentation available


- **login_stage_two**(self, hashed_answer, original_challenge):

				No documentation available


- **login**(self, challenge):

				No documentation available


- **on_login**(self):

				No documentation available


Authentication_Table
--------------

	 Provides an additional factor of authentication. During account
        registration, the server generates an Authentication_Table for the
        newly registered client. The server records this table and sends a 
        copy to the client. When the client attempts to login, the server
        generates a random selection of indices and sends these to the client.
        The client is supposed to return the appropriate symbols from the
        table and the server matches what it expected against the response.
        
        Acts as "something you have", albeit in the form of data. 


Method resolution order: 

	(<class 'pride.authentication2.Authentication_Table'>, <type 'object'>)

- **load**(cls, text):

		 Load a bytestream as returned by Authenticated_Table.save and 
            return an authenticated table object. 


- **compare**(calculation, response):

		 Compares two iterables in constant time 


- **get_passcode**(self, *args):

		 Returns a passcode generated from the symbols located at the 
            indices specified in the challenge


- **generate_challenge**(count):

		 Generates count random pairs of indices, which range from 0-15 


- **save**(self, _file):

		 Saves the table information to a bytestream. If _file is supplied,
            the bytestream is dumped to the file instead of returned.
            
            WARNING: This bytestream is a secret that authenticates a username
            and should be protected as any password or secure information. 


Instruction
--------------

	 usage: Instruction(component_name, method_name,
                           *args, **kwargs).execute(priority=priority,
                                                    callback=callback)

            - component_name is the string reference of the component
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.


        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will be performed. Instructions are useful for explicitly
        timed/recurring tasks.

        Instructions may be reused. The same instruction object can be
        executed any number of times.

        Note that Instructions must be executed to have any effect, and
        that they do not happen inline even if the priority is 0.0. In
        order to access the result of the executed function, a callback
        function can be provided.


Method resolution order: 

	(<class 'pride.Instruction'>, <type 'object'>)

- **execute**(self, priority, callback):

		 usage: instruction.execute(priority=0.0, callback=None)

            Submits an instruction to the processing queue.
            The instruction will be executed in priority seconds.
            An optional callback function can be provided if the return value
            of the instruction is needed. 


- **purge**(cls, reference):

				No documentation available


- **unschedule**(self):

				No documentation available


SecurityError
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.SecurityError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

UnauthorizedError
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.UnauthorizedError'>,
	 <class 'pride.errors.SecurityError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

hash_function
--------------

**hash_function**(algorithm_name, backend):

		 Returns a Hash object of type algorithm_name from 
            cryptography.hazmat.primitives.hashes 


remote_procedure_call
--------------

**new_call**(args, **kwargs):

				No documentation available


test_Authenticated_Service2
--------------

**test_Authenticated_Service2**():

				No documentation available
