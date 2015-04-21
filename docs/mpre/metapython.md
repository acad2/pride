mpre.metapython
========
 Launcher script for the Metapython runtime environment. This script starts a metapython     
    session, and the first positional argument supplied is interpreted as the filepath of the
    python script to execute

Shell
--------
	 Provides the client side of the interpreter session. Handles keystrokes and
	sends them to the Interpreter_Service to be executed.

Default values for newly created instances:

- username                 : root
- prompt                   : >>> 
- target                   : Interpreter_Service
- memory_mode              : -1
- deleted                  : False
- verbosity                : 
- startup_definitions      : 
- memory_size              : 4096
- password                 : password
- email                    : 

This object defines the following non-private methods:


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


This objects method resolution order is:

(class 'mpre._metapython.Shell', class 'mpre.network2.Authenticated_Client', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')
