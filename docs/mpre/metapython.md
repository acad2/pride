mpre.metapython
==============

 Launcher script for the Metapython runtime environment. This script starts a metapython     
    session, and the first positional argument supplied is interpreted as the filepath of the
    python script to execute

Shell
--------------

	 Provides the client side of the interpreter session. Handles keystrokes and
        sends them to the Interpreter_Service to be executed.


Instance defaults: 

	{'_deleted': False,
	 'email': '',
	 'password': 'password',
	 'prompt': '>>> ',
	 'replace_reference_on_load': True,
	 'startup_definitions': '',
	 'target': 'Interpreter_Service',
	 'username': 'root',
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre._metapython.Shell'>,
	 <class 'mpre.network2.Authenticated_Client'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **handle_startup_definitions**(self):

		No documentation available


- **login_result**(self, sender, packet):

		No documentation available


- **exec_code_request**(self, sender, source):

		No documentation available


- **result**(self, sender, packet):

		No documentation available


- **execute_source**(self, source):

		No documentation available


- **handle_keystrokes**(self, sender, keyboard_input):

		No documentation available
