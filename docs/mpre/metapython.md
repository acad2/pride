mpre.metapython
==============

 Launcher script for the Metapython runtime environment. This script starts a metapython     
    session, and the first positional argument supplied is interpreted as the filepath of the
    python script to execute. .

Shell
--------------

	 Provides the client side of the interpreter session. Handles keystrokes and
        sends them to the Interpreter_Service to be executed.


Instance defaults: 

	{'_deleted': False,
	 'auto_login': True,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'host_info': ('localhost', 40022),
	 'logged_in': False,
	 'password': 'password',
	 'password_prompt': 'Please provide the pass phrase or word: ',
	 'prompt': '>>> ',
	 'protocol_client': 'mpre.srp.SRP_Client',
	 'replace_reference_on_load': True,
	 'startup_definitions': '',
	 'target_service': 'Interpreter_Service',
	 'username': 'root',
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre._metapython.Shell'>,
	 <class 'mpre.authentication.Authenticated_Client'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **handle_startup_definitions**(self):

				No documentation available


- **execute_source**(self, source):

				No documentation available


- **on_login**(self, message):

				No documentation available


- **handle_keystrokes**(self, keyboard_input):

				No documentation available


- **result**(self, packet):

				No documentation available
