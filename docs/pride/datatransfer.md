pride.datatransfer
==============

 pride.datatransfer - Authenticated services for transferring data on a network
    Constructs a service for the transfer of arbitrary data from one registered 
    party to another. 

Background_Refresh
--------------

	No docstring found


Instance defaults: 

	{'_run_queued': False,
	 'context_managed': False,
	 'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'priority': 0.5,
	 'replace_reference_on_load': True,
	 'reschedule_run_after_exception': True,
	 'run_callback': None,
	 'run_condition': '',
	 'running': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.datatransfer.Background_Refresh'>,
	 <class 'pride.vmlibrary.Process'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **run**(self):

				No documentation available


Data_Transfer_Client
--------------

	 Client program for sending data securely to a party registered
        with the target service. 


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
	 'target_service': '/Python/Data_Transfer_Service',
	 'token_file_encrypted': True,
	 'token_file_indexable': False,
	 'token_file_type': 'pride.fileio.Database_File',
	 'username_prompt': '{}: Please provide the user name for {}@{}: '}

Method resolution order: 

	(<class 'pride.datatransfer.Data_Transfer_Client'>,
	 <class 'pride.authentication2.Authenticated_Client'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **receive**(self, messages):

		 Receives messages and supplies them to alert for user notification.
            self.verbosity may feature usernames of other clients; entries not
            found default to 0. 


- **_make_rpc**(self, *args, **kwargs):

				No documentation available


- **refresh**(self):

		 Checks for new data from the server 


Data_Transfer_Service
--------------

	 Service for transferring arbitrary data from one registered client to another 


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

	(<class 'pride.datatransfer.Data_Transfer_Service'>,
	 <class 'pride.authentication2.Authenticated_Service'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **send_to**(self, receiver, message):

				No documentation available


File_Storage_Daemon
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
	 'file_type': '',
	 'hash_function': 'SHA256',
	 'hkdf_table_update_info_string': 'Authentication Table Update',
	 'ip': 'localhost',
	 'parse_args': False,
	 'password_prompt': '{}: Please provide the pass phrase or word for {}@{}: ',
	 'port': 40022,
	 'replace_reference_on_load': True,
	 'shared_key_size': 32,
	 'startup_components': (),
	 'target_service': '/Python/Data_Transfer_Service',
	 'token_file_encrypted': True,
	 'token_file_indexable': False,
	 'token_file_type': 'pride.fileio.Database_File',
	 'username': 'File_Storage_Daemon',
	 'username_prompt': '{}: Please provide the user name for {}@{}: '}

Method resolution order: 

	(<class 'pride.datatransfer.File_Storage_Daemon'>,
	 <class 'pride.datatransfer.Data_Transfer_Client'>,
	 <class 'pride.authentication2.Authenticated_Client'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **receive**(self, message):

				No documentation available


File_Transfer
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
	 'file': None,
	 'file_type': 'open',
	 'filename': '',
	 'hash_function': 'SHA256',
	 'hkdf_table_update_info_string': 'Authentication Table Update',
	 'ip': 'localhost',
	 'parse_args': False,
	 'password_prompt': '{}: Please provide the pass phrase or word for {}@{}: ',
	 'permission_string': "{}:{} Accept file transfer from '{}'?\n'{}' ({} bytes) ",
	 'port': 40022,
	 'receivers': (),
	 'replace_reference_on_load': True,
	 'shared_key_size': 32,
	 'startup_components': (),
	 'target_service': '/Python/Data_Transfer_Service',
	 'token_file_encrypted': True,
	 'token_file_indexable': False,
	 'token_file_type': 'pride.fileio.Database_File',
	 'username_prompt': '{}: Please provide the user name for {}@{}: '}

Method resolution order: 

	(<class 'pride.datatransfer.File_Transfer'>,
	 <class 'pride.datatransfer.Data_Transfer_Client'>,
	 <class 'pride.authentication2.Authenticated_Client'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **receive**(self, messages):

				No documentation available


Proxy
--------------

	No docstring found


Instance defaults: 

	{'_register_results': None,
	 '_user_database': '',
	 'authentication_table_size': 256,
	 'auto_login': True,
	 'auto_register': True,
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
	 'target_service': '/Python/Data_Transfer_Service',
	 'token_file_encrypted': True,
	 'token_file_indexable': False,
	 'token_file_type': 'pride.fileio.Database_File',
	 'username': 'Proxy',
	 'username_prompt': '{}: Please provide the user name for {}@{}: '}

Method resolution order: 

	(<class 'pride.datatransfer.Proxy'>,
	 <class 'pride.datatransfer.Data_Transfer_Client'>,
	 <class 'pride.authentication2.Authenticated_Client'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **receive**(self, messages):

				No documentation available


file_operation
--------------

**file_operation**(filename, mode, method, file_type, offset, data):

				No documentation available


test_File_Transfer
--------------

**test_File_Transfer**():

				No documentation available


test_dts
--------------

**test_dts**():

				No documentation available
