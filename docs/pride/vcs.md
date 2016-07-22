pride.vcs
==============



Version_Control
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

	(<class 'pride.vcs.Version_Control'>,
	 <class 'pride.authentication2.Authenticated_Service'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **load_module**(self, module_name, module_id, repo_id):

				No documentation available


- **save_module**(self, module_name, module_source, module_id, repo_id):

				No documentation available
