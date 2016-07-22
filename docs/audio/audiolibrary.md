audio.audiolibrary
==============



Audio_Manager
--------------

	No docstring found


Instance defaults: 

	{'config_file_name': '',
	 'configure': False,
	 'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': (),
	 'use_defaults': True}

Method resolution order: 

	(<class 'audio.audiolibrary.Audio_Manager'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **load_api**(self):

				No documentation available


- **get_devices**(self, devices):

				No documentation available


- **load_default_devices**(self):

				No documentation available


- **run_configuration**(self, exit_when_finished):

				No documentation available


- **record**(self, device_name, audio_file):

				No documentation available


- **load_config_file**(self):

				No documentation available


Audio_Reactor
--------------

	No docstring found


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'source_name': '',
	 'startup_components': ()}

Method resolution order: 

	(<class 'audio.audiolibrary.Audio_Reactor'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **handle_audio_input**(self, audio_data):

				No documentation available


- **add_listener**(self, reference):

				No documentation available


- **handle_end_of_stream**(self):

				No documentation available


- **handle_audio_output**(self, audio_data):

				No documentation available


- **set_input_device**(self, target_reference):

				No documentation available


- **remove_listener**(self, reference):

				No documentation available


Config_Utility
--------------

	No docstring found


Instance defaults: 

	{'_run_queued': False,
	 'config_file_name': 'audiocfg',
	 'context_managed': False,
	 'deleted': False,
	 'dont_save': False,
	 'mode': ('input',),
	 'parse_args': False,
	 'priority': 0.04,
	 'replace_reference_on_load': True,
	 'reschedule_run_after_exception': True,
	 'run_callback': None,
	 'run_condition': '',
	 'running': False,
	 'startup_components': ()}

Method resolution order: 

	(<class 'audio.audiolibrary.Config_Utility'>,
	 <class 'pride.vmlibrary.Process'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **run**(self):

				No documentation available


- **print_display_devices**(self, device_dict):

				No documentation available


- **write_config_file**(self, device_list):

				No documentation available


- **get_selections**(self):

				No documentation available


Instruction
--------------

	 usage: Instruction(component_name, method_name,
                           *args, **kwargs).execute(priority=priority,
                                                    callback=callback)

            - component_name is the string reference of the component
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.


        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will be performed. Instructions are useful for explicitly
        timed/recurring tasks.

        Instructions may be reused. The same instruction object can be
        executed any number of times.

        Note that Instructions must be executed to have any effect, and
        that they do not happen inline even if the priority is 0.0. In
        order to access the result of the executed function, a callback
        function can be provided.


Method resolution order: 

	(<class 'pride.Instruction'>, <type 'object'>)

- **execute**(self, priority, callback):

		 usage: instruction.execute(priority=0.0, callback=None)

            Submits an instruction to the processing queue.
            The instruction will be executed in priority seconds.
            An optional callback function can be provided if the return value
            of the instruction is needed. 


- **purge**(cls, reference):

				No documentation available


- **unschedule**(self):

				No documentation available


Latency
--------------

	 usage: Latency([name="component_name"], 
                       [size=20]) => latency_object
                       
        Latency objects possess a start_measuring and )


Method resolution order: 

	(<class 'pride.datastructures.Latency'>, <type 'object'>)

- **mark**(self):

				No documentation available


Wav_File
--------------

	No docstring found


Instance defaults: 

	{'channels': 2,
	 'deleted': False,
	 'dont_save': False,
	 'filename': '',
	 'mode': 'rb',
	 'parse_args': False,
	 'rate': 48000,
	 'repeat': False,
	 'replace_reference_on_load': True,
	 'sample_width': 2,
	 'source_name': '',
	 'startup_components': ()}

Method resolution order: 

	(<class 'audio.audiolibrary.Wav_File'>,
	 <class 'audio.audiolibrary.Audio_Reactor'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **handle_audio_input**(self, audio_input):

				No documentation available


- **read**(self, size):

				No documentation available


- **close**(self):

				No documentation available


- **tell**(self):

				No documentation available


- **write**(self, data):

				No documentation available


record_wav_file
--------------

**record_wav_file**(parse_args, **kwargs):

				No documentation available


wav_file_info
--------------

**wav_file_info**(parse_args, **kwargs):

				No documentation available
