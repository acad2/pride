mpre.voip
==============



Message_Client
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'auto_login': True,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'ip': 'localhost',
	 'logged_in': False,
	 'name': 'messenger',
	 'password': '',
	 'password_prompt': '{}: Please provide the pass phrase or word: ',
	 'port': 40022,
	 'protocol_client': 'mpre.srp.SRP_Client',
	 'replace_reference_on_load': True,
	 'target_service': 'Message_Server',
	 'username': ''}

Method resolution order: 

	(<class 'mpre.voip.Message_Client'>,
	 <class 'mpre.authentication.Authenticated_Client'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **receive_message**(self, sender, message):

				No documentation available


- **handle_input**(self, keystrokes):

				No documentation available


Message_Server
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'allow_registration': True,
	 'contact_lists': None,
	 'database_name': '',
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'login_message': '',
	 'mailbox': None,
	 'protocol_component': 'Secure_Remote_Password',
	 'replace_reference_on_load': True,
	 'requester_address': None}

Method resolution order: 

	(<class 'mpre.voip.Message_Server'>,
	 <class 'mpre.authentication.Authenticated_Service'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **register**(self, username, password):

				No documentation available


- **call**(instance, *args, **kwargs):

				No documentation available


- **call**(instance, *args, **kwargs):

				No documentation available
