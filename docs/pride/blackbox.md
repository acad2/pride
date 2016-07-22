pride.blackbox
==============

 Provides network services that do not reveal information about how 
    application logic produces its result. Black_Box_Services receive input
    in the form of keystrokes, mouse clicks, and potentially audio,
    operate on the input in a manner opaque to the client, and return output
    to the client. 

Black_Box_Client
--------------

	No docstring found


Instance defaults: 

	{'_register_results': None,
	 '_user_database': '',
	 'audio_source': '/Python/Audio_Manager/Audio_Input',
	 'audio_support': False,
	 'authentication_table_size': 256,
	 'auto_login': True,
	 'challenge_size': 9,
	 'deleted': False,
	 'dont_save': False,
	 'hash_function': 'SHA256',
	 'hkdf_table_update_info_string': 'Authentication Table Update',
	 'ip': 'localhost',
	 'microphone_on': False,
	 'mouse_support': False,
	 'parse_args': False,
	 'password_prompt': '{}: Please provide the pass phrase or word for {}@{}: ',
	 'port': 40022,
	 'refresh_interval': 0.95,
	 'replace_reference_on_load': True,
	 'response_methods': ('handle_response_draw',),
	 'shared_key_size': 32,
	 'startup_components': (),
	 'target_service': '/Python/Black_Box_Service',
	 'token_file_encrypted': True,
	 'token_file_indexable': False,
	 'token_file_type': 'pride.fileio.Database_File',
	 'username_prompt': '{}: Please provide the user name for {}@{}: '}

Method resolution order: 

	(<class 'pride.blackbox.Black_Box_Client'>,
	 <class 'pride.authentication2.Authenticated_Client'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **handle_response_draw**(self, draw_instructions):

				No documentation available


- **handle_audio_input**(self, audio_bytes):

				No documentation available


- **_make_rpc**(self, *args, **kwargs):

				No documentation available


- **handle_keyboard_input**(self, input_bytes):

				No documentation available


- **receive_response**(self, packet):

				No documentation available


- **handle_mouse_input**(self, mouse_info):

				No documentation available


Black_Box_Service
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
	 'input_types': ('keyboard', 'mouse', 'audio'),
	 'login_message': 'Welcome to the {}, {} from {}',
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'shared_key_size': 32,
	 'startup_components': (),
	 'validation_failure_string': ".validate: Authorization Failure:\n    ip blacklisted: {}    ip whitelisted: {}\n    session_id logged in: {}\n    method_name: '{}'    method available remotely: {}\n    login allowed: {}    registration allowed: {}",
	 'window_type': 'pride.gui.sdllibrary.Window_Context'}

Method resolution order: 

	(<class 'pride.blackbox.Black_Box_Service'>,
	 <class 'pride.authentication2.Authenticated_Service'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **handle_audio_input**(self, audio_bytes):

				No documentation available


- **on_login**(self):

				No documentation available


- **handle_input**(self, packed_user_input):

				No documentation available


- **handle_keyboard_input**(self, input_bytes):

				No documentation available


- **handle_mouse_input**(self, mouse_info):

				No documentation available


Event_Structure
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.blackbox.Event_Structure'>, <type 'object'>)

Mouse_Structure
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.blackbox.Mouse_Structure'>, <type 'object'>)

test_black_box_service
--------------

**test_black_box_service**():

				No documentation available
