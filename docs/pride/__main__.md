__main__
==============

 Provides an entry point to the environment and a shell connection for interacting with it. 

Documentation
--------------

	No docstring found


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': (),
	 'top_level_package': ''}

Method resolution order: 

	(<class '__main__.Documentation'>, <class 'pride.base.Base'>, <type 'object'>)

- **write_yml_entry**(self, entry, yml_file):

				No documentation available


- **write_markdown_file**(self, markdown_text, filename):

				No documentation available


Interpreter
--------------

	 Executes python source. Requires authentication from remote hosts. 
        The source code and return value of all requests are logged. 


Instance defaults: 

	{'_logger_type': 'StringIO.StringIO',
	 'allow_login': True,
	 'allow_registration': False,
	 'authentication_table_size': 256,
	 'challenge_size': 9,
	 'database_name': '',
	 'database_type': 'pride.database.Database',
	 'deleted': False,
	 'dont_save': False,
	 'hash_function': 'SHA256',
	 'help_string': 'Type "help", "copyright", "credits" or "license" for more information.',
	 'hkdf_table_update_info_string': 'Authentication Table Update',
	 'login_message': 'Welcome {} from {}\nPython {} on {}\n{}\n',
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'shared_key_size': 32,
	 'startup_components': (),
	 'validation_failure_string': ".validate: Authorization Failure:\n    ip blacklisted: {}    ip whitelisted: {}\n    session_id logged in: {}\n    method_name: '{}'    method available remotely: {}\n    login allowed: {}    registration allowed: {}"}

Method resolution order: 

	(<class 'pride.interpreter.Interpreter'>,
	 <class 'pride.authentication2.Authenticated_Service'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **execute_instruction**(self, instruction, priority, callback):

		 Executes the supplied instruction with the specified priority and callback 


- **execute_source**(self, source):

				No documentation available


- **on_login**(self):

				No documentation available


Package
--------------

	No docstring found


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'ignore_modules': (),
	 'include_documentation': False,
	 'include_source': True,
	 'package_name': None,
	 'parse_args': False,
	 'python_extensions': ('.py', '.pyx', '.pyd', '.pso', '.so'),
	 'replace_reference_on_load': False,
	 'required_modules': (),
	 'required_packages': (),
	 'startup_components': (),
	 'top_level_package': ''}

Method resolution order: 

	(<class '__main__.Package'>, <class 'pride.base.Base'>, <type 'object'>)

- **find_module**(self, module_name, path):

				No documentation available


- **load_module**(self, module_name):

				No documentation available


Python
--------------

	 The "main" class. Provides an entry point to the environment. 
        Instantiating this component and calling the start_machine method 
        starts the execution of the Processor component.


Instance defaults: 

	{'command': '',
	 'deleted': False,
	 'dont_save': False,
	 'environment_setup': ('PYSDL2_DLL_PATH = c:\\users\\_\\pythonbs\\pride\\gui\\',),
	 'interpreter_type': 'pride.interpreter.Interpreter',
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': ('pride.vcs.Version_Control',
	                        'pride.vmlibrary.Processor',
	                        'pride.fileio.File_System',
	                        'pride.network.Network_Connection_Manager',
	                        'pride.network.Network',
	                        'pride.interpreter.Interpreter',
	                        'pride.rpc.Rpc_Connection_Manager',
	                        'pride.rpc.Rpc_Server',
	                        'pride.rpc.Rpc_Worker',
	                        'pride.datatransfer.Data_Transfer_Service',
	                        'pride.datatransfer.Background_Refresh'),
	 'startup_definitions': ''}

Method resolution order: 

	(<class 'pride.interpreter.Python'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **start_machine**(self):

		 Begins the processing of Instruction objects.


- **exit**(self, exit_code):

				No documentation available


- **setup_os_environ**(self):

		 This method is called automatically in Python.__init__; os.environ can
            be customized on startup via modifying Python.defaults["environment_setup"].
            This can be useful for modifying system path only for the duration of the applications run time.
            Currently this is only used to point to this files directory for SDL2 dll files. 


Shell
--------------

	 Handles keystrokes and sends python source to the Interpreter to 
        be executed. This requires authentication via username/password.


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
	 'password': '',
	 'password_prompt': '{}: Please provide the pass phrase or word for {}@{}: ',
	 'port': 40022,
	 'replace_reference_on_load': True,
	 'shared_key_size': 32,
	 'startup_components': (),
	 'startup_definitions': 'import pride.base\nimport pride\n\nfrom pride.utilities import documentation, usage\n\ndef open_firefox():\n    try:\n        import selenium.webdriver\n    except ImportError:\n        pass\n    else:\n        return selenium.webdriver.Firefox()\n        \ndef create(instance_type, *args, **kwargs):\n    return objects["/Python"].create(instance_type, *args, **kwargs)\n\ndef delete(reference):\n    objects[reference].delete()     \n\ndef logout(program="/User/Shell"):\n    objects[program].logout()\n    \n#import pride.audio\n#pride.audio.enable()\nimport pride.gui\n#window = pride.gui.enable()\n\n#graph = objects["/Python/SDL_Window"].create("pride.gui.graph.Graph")\n#explorer = objects["/Python/SDL_Window"].create("pride.gui.fileexplorer.File_Explorer")\n#chess = objects["/Python/SDL_Window"].create("pride.gui.chess.Chess")\n#cyvasse = objects[window].create("pride.gui.cyvasse.Cyvasse")\n#messenger = objects[window].create("pride.gui.messenger.Messenger", username="Ella")\n#homescreen = objects[window].create(\'pride.gui.widgetlibrary.Homescreen\')\n#visualized_list = objects[window].create("pride.gui.datatypes.List")\n',
	 'stdout': None,
	 'target_service': '/Python/Interpreter',
	 'token_file_encrypted': True,
	 'token_file_indexable': False,
	 'token_file_type': 'pride.fileio.Database_File',
	 'username': 'localhost',
	 'username_prompt': '{}: Please provide the user name for {}@{}: '}

Method resolution order: 

	(<class 'pride.interpreter.Shell'>,
	 <class 'pride.authentication2.Authenticated_Client'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **_make_rpc**(self, *args, **kwargs):

				No documentation available


- **on_login**(self, message):

				No documentation available


- **handle_result**(self, packet):

				No documentation available


- **handle_startup_definitions**(self):

				No documentation available


build_documentation_site
--------------

**build_documentation_site**(module):

				No documentation available


create_module
--------------

**create_module**(module_name, source, context):

		 Creates a module with the supplied name and source


main_as_name
--------------

**main_as_name**(args, **kwds):

				No documentation available
