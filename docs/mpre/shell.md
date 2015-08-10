mpre.shell
==============



Command_Line
--------------

	 Captures user input and provides the input to the specified or default program.
    
        Available programs can be modified via the add_program, remove_program,
        set_default_program, and get_program methods.


Instance defaults: 

	{'_deleted': False,
	 'auto_start': True,
	 'default_programs': ('mpre.shell.Shell_Program',
	                      'mpre.shell.Switch_Program',
	                      'mpre.shell.File_Explorer',
	                      'mpre.programs.register.Registration'),
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'priority': 0.04,
	 'programs': None,
	 'prompt': '>>> ',
	 'replace_reference_on_load': True,
	 'run_callback': None,
	 'running': True,
	 'thread_started': False,
	 'write_prompt': True}

Method resolution order: 

	(<class 'mpre.shell.Command_Line'>,
	 <class 'mpre.vmlibrary.Process'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **add_program**(self, program_name, callback_info):

				No documentation available


- **run**(self):

				No documentation available


- **read_input**(self):

				No documentation available


- **on_load**(self, attributes):

				No documentation available


- **set_prompt**(self, prompt):

				No documentation available


- **remove_program**(self, program_name):

				No documentation available


- **set_default_program**(self, callback_info, set_backup):

				No documentation available


- **get_program**(self, program_name):

				No documentation available


File_Explorer
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'name': 'file_explorer',
	 'replace_reference_on_load': True,
	 'set_as_default': False}

Method resolution order: 

	(<class 'mpre.shell.File_Explorer'>,
	 <class 'mpre.shell.Program'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **listdir**(self, directory_name, mode):

				No documentation available


Program
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'name': '',
	 'replace_reference_on_load': True,
	 'set_as_default': False}

Method resolution order: 

	(<class 'mpre.shell.Program'>, <class 'mpre.base.Base'>, <type 'object'>)

- **handle_input**(self, input):

				No documentation available


- **help**(self, input):

				No documentation available


Shell_Program
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'name': 'shell',
	 'replace_reference_on_load': True,
	 'set_as_default': False,
	 'use_shell': True}

Method resolution order: 

	(<class 'mpre.shell.Shell_Program'>,
	 <class 'mpre.shell.Program'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **handle_input**(self, input):

				No documentation available


Switch_Program
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'name': 'switch',
	 'replace_reference_on_load': True,
	 'set_as_default': False}

Method resolution order: 

	(<class 'mpre.shell.Switch_Program'>,
	 <class 'mpre.shell.Program'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **handle_input**(self, input):

				No documentation available


get_permission
--------------

**get_permission**(prompt):

		 Displays prompt to the user. Attempts to infer whether or not the supplied
        user input is affirmative or negative via shell.is_affirmative. 


get_selection
--------------

**get_selection**(prompt, answers):

		 Displays prompt to the user. Only input from the supplied answers iterable
        will be accepted. bool may be specified as answers in order to extract
        a True/False response. 


get_user_input
--------------

**get_user_input**(prompt):

		 raw_input function that plays nicely when sys.stdout is swapped 


is_affirmative
--------------

**is_affirmative**(input, affirmative_words):

		 Attempt to infer whether the supplied input is affirmative. 
