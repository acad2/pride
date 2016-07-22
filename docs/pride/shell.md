pride.shell
==============



CA_Screensaver
--------------

	No docstring found


Instance defaults: 

	{'_injection_timer': 0,
	 '_run_queued': False,
	 'context_managed': False,
	 'deleted': False,
	 'dont_save': False,
	 'file_text': '',
	 'newline_scalar': 1.5,
	 'parse_args': False,
	 'priority': 0.08,
	 'rate': 3,
	 'replace_reference_on_load': True,
	 'reschedule_run_after_exception': True,
	 'run_callback': None,
	 'run_condition': '',
	 'running': True,
	 'startup_components': (),
	 'storage_size': 80}

Method resolution order: 

	(<class 'pride.shell.CA_Screensaver'>,
	 <class 'pride.shell.Terminal_Screensaver'>,
	 <class 'pride.vmlibrary.Process'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **run**(self):

				No documentation available


Command_Line
--------------

	 Captures user input and provides the input to the specified or default program.
    
        Available programs can be modified via the add_program, remove_program,
        set_default_program, and get_program methods.


Instance defaults: 

	{'_run_queued': False,
	 'context_managed': False,
	 'default_programs': ('pride.shell.OS_Shell', 'pride.shell.Switch_Program'),
	 'deleted': False,
	 'dont_save': False,
	 'idle_threshold': 10000,
	 'parse_args': False,
	 'priority': 0.04,
	 'programs': None,
	 'prompt': '>>> ',
	 'replace_reference_on_load': True,
	 'reschedule_run_after_exception': True,
	 'run_callback': None,
	 'run_condition': '',
	 'running': True,
	 'screensaver_type': 'pride.shell.CA_Screensaver',
	 'startup_components': (),
	 'thread_started': False,
	 'write_prompt': True}

Method resolution order: 

	(<class 'pride.shell.Command_Line'>,
	 <class 'pride.vmlibrary.Process'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **run**(self):

				No documentation available


- **handle_idle**(self):

				No documentation available


- **add_program**(self, program_name, callback_info):

				No documentation available


- **read_input**(self):

				No documentation available


- **on_load**(self, attributes):

				No documentation available


- **clear**(self):

				No documentation available


- **set_prompt**(self, prompt):

				No documentation available


- **remove_program**(self, program_name):

				No documentation available


- **set_default_program**(self, name, callback_info, set_backup):

				No documentation available


- **get_program**(self, program_name):

				No documentation available


Matrix_Screensaver
--------------

	No docstring found


Instance defaults: 

	{'_run_queued': False,
	 'context_managed': False,
	 'deleted': False,
	 'dont_save': False,
	 'file_text': '',
	 'newline_scalar': 1.5,
	 'parse_args': False,
	 'priority': 0.08,
	 'rate': 3,
	 'replace_reference_on_load': True,
	 'reschedule_run_after_exception': True,
	 'run_callback': None,
	 'run_condition': '',
	 'running': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.shell.Matrix_Screensaver'>,
	 <class 'pride.shell.Terminal_Screensaver'>,
	 <class 'pride.vmlibrary.Process'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **run**(self):

				No documentation available


Messenger_Program
--------------

	No docstring found


Instance defaults: 

	{'command_line': '/User/Command_Line',
	 'deleted': False,
	 'dont_save': False,
	 'name': 'messenger',
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'set_as_default': False,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.shell.Messenger_Program'>,
	 <class 'pride.shell.Program'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **handle_input**(self, user_input):

				No documentation available


OS_Shell
--------------

	No docstring found


Instance defaults: 

	{'command_line': '/User/Command_Line',
	 'deleted': False,
	 'dont_save': False,
	 'name': 'os_shell',
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'set_as_default': False,
	 'startup_components': (),
	 'use_shell': True}

Method resolution order: 

	(<class 'pride.shell.OS_Shell'>,
	 <class 'pride.shell.Program'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **handle_input**(self, input):

				No documentation available


Program
--------------

	No docstring found


Instance defaults: 

	{'command_line': '/User/Command_Line',
	 'deleted': False,
	 'dont_save': False,
	 'name': '',
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'set_as_default': False,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.shell.Program'>, <class 'pride.base.Base'>, <type 'object'>)

- **help**(self, input):

				No documentation available


- **set_as_default_program**(self):

				No documentation available


- **handle_input**(self, input):

				No documentation available


- **add_to_programs**(self):

				No documentation available


Python_Shell
--------------

	No docstring found


Instance defaults: 

	{'command_line': '/User/Command_Line',
	 'deleted': False,
	 'dont_save': False,
	 'name': 'python',
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'set_as_default': False,
	 'shell_connection': '/User/Shell',
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.shell.Python_Shell'>,
	 <class 'pride.shell.Program'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **handle_input**(self, user_input):

				No documentation available


Random_Screensaver
--------------

	No docstring found


Instance defaults: 

	{'_run_queued': False,
	 'context_managed': False,
	 'deleted': False,
	 'dont_save': False,
	 'file_text': '',
	 'newline_scalar': 1.5,
	 'parse_args': False,
	 'priority': 0.08,
	 'rate': 3,
	 'replace_reference_on_load': True,
	 'reschedule_run_after_exception': True,
	 'run_callback': None,
	 'run_condition': '',
	 'running': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.shell.Random_Screensaver'>,
	 <class 'pride.shell.Terminal_Screensaver'>,
	 <class 'pride.vmlibrary.Process'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

Switch_Program
--------------

	No docstring found


Instance defaults: 

	{'command_line': '/User/Command_Line',
	 'deleted': False,
	 'dont_save': False,
	 'name': 'switch',
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'set_as_default': False,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.shell.Switch_Program'>,
	 <class 'pride.shell.Program'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **handle_input**(self, input):

				No documentation available


Terminal_Screensaver
--------------

	No docstring found


Instance defaults: 

	{'_run_queued': False,
	 'context_managed': False,
	 'deleted': False,
	 'dont_save': False,
	 'file_text': '',
	 'newline_scalar': 1.5,
	 'parse_args': False,
	 'priority': 0.08,
	 'rate': 3,
	 'replace_reference_on_load': True,
	 'reschedule_run_after_exception': True,
	 'run_callback': None,
	 'run_condition': '',
	 'running': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.shell.Terminal_Screensaver'>,
	 <class 'pride.vmlibrary.Process'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **run**(self):

				No documentation available


Wave_CAtest
--------------

	No docstring found


Instance defaults: 

	{'_run_queued': False,
	 'context_managed': False,
	 'deleted': False,
	 'dont_save': False,
	 'file_text': '',
	 'newline_scalar': 1.5,
	 'parse_args': False,
	 'priority': 0.08,
	 'rate': 3,
	 'replace_reference_on_load': True,
	 'reschedule_run_after_exception': True,
	 'run_callback': None,
	 'run_condition': '',
	 'running': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.shell.Wave_CAtest'>,
	 <class 'pride.shell.Terminal_Screensaver'>,
	 <class 'pride.vmlibrary.Process'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **run**(self):

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


is_affirmative
--------------

**is_affirmative**(input, affirmative_words):

		 Attempt to infer whether the supplied input is affirmative. 
