pride.recordservice
==============



Record_Service
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
	 'hash_type': 'SHA512',
	 'hkdf_table_update_info_string': 'Authentication Table Update',
	 'login_message': 'Welcome to the {}, {} from {}',
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'shared_key_size': 32,
	 'startup_components': (),
	 'validation_failure_string': ".validate: Authorization Failure:\n    ip blacklisted: {}    ip whitelisted: {}\n    session_id logged in: {}\n    method_name: '{}'    method available remotely: {}\n    login allowed: {}    registration allowed: {}"}

Method resolution order: 

	(<class 'pride.recordservice.Record_Service'>,
	 <class 'pride.authentication2.Authenticated_Service'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **hash**(self, file_data):

				No documentation available


- **save_record**(self, access, file_data, filename, file_description):

				No documentation available


- **load_record**(self, access, filename, file_description):

				No documentation available


Record_Service_Client
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
	 'target_service': '/Python/Record_Service',
	 'token_file_encrypted': False,
	 'token_file_indexable': True,
	 'token_file_type': 'pride.fileio.Database_File',
	 'username_prompt': '{}: Please provide the user name for {}@{}: '}

Method resolution order: 

	(<class 'pride.recordservice.Record_Service_Client'>,
	 <class 'pride.authentication2.Authenticated_Client'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **_make_rpc**(self, *args, **kwargs):

				No documentation available


- **_make_rpc**(self, *args, **kwargs):

				No documentation available


- **display_record**(self, records):

				No documentation available


test_Record_Service
--------------

**test_Record_Service**():

				No documentation available
