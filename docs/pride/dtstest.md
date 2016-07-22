pride.dtstest
==============



Secure_Data_Transfer_Client
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
	 'ecdh_curve_name': 'SECP384R1',
	 'hash_function': 'SHA256',
	 'hkdf_table_update_info_string': 'Authentication Table Update',
	 'ip': 'localhost',
	 'keysize': 384,
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

	(<class 'pride.dtstest.Secure_Data_Transfer_Client'>,
	 <class 'pride.datatransfer.Data_Transfer_Client'>,
	 <class 'pride.authentication2.Authenticated_Client'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **initiate_key_exchange**(self, username):

				No documentation available


- **new_keypair**(self):

				No documentation available


- **receive**(self, messages):

				No documentation available


load_pem_public_key
--------------

**load_pem_public_key**(data, backend):

				No documentation available


test_secure_data_transfer_client
--------------

**test_secure_data_transfer_client**():

				No documentation available
