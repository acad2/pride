mpre.metapython
==============

 Launcher script for the Metapython runtime environment. This script starts a metapython     
    session, and the first positional argument supplied is interpreted as the filepath of the
    python script to execute. .

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
