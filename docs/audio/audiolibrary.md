audiolibrary
==============



Audio_File
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'directory': None,
	 'file': None,
	 'file_system': 'disk',
	 'file_type': 'StringIO.StringIO',
	 'is_directory': False,
	 'mode': '',
	 'path': '',
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'audiolibrary.Audio_File'>,
	 <class 'mpre.fileio.File'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **handle_audio_input**(self, sender, audio_data):

		No documentation available


Audio_Manager
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'config_file_name': '',
	 'configure': False,
	 'replace_reference_on_load': True,
	 'use_defaults': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'audiolibrary.Audio_Manager'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **load_api**(self):

		No documentation available


- **load_default_devices**(self):

		No documentation available


- **record**(self, device_name, file, channels, rate):

		No documentation available


- **run_configuration**(self, exit_when_finished):

		No documentation available


- **load_config_file**(self):

		No documentation available


- **get_devices**(self, devices):

		No documentation available


Audio_Reactor
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'replace_reference_on_load': True,
	 'source_name': '',
	 'verbosity': ''}

Method resolution order: 

	(<class 'audiolibrary.Audio_Reactor'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **add_listener**(self, instance_name):

		No documentation available


- **handle_audio_output**(self, audio_data):

		No documentation available


- **handle_audio_input**(self, sender, audio_data):

		No documentation available


- **set_input_device**(self, target_instance_name):

		No documentation available


- **handle_end_of_stream**(self):

		No documentation available


- **remove_listener**(self, instance_name):

		No documentation available


Config_Utility
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'auto_start': False,
	 'config_file_name': 'audiocfg',
	 'mode': ('input',),
	 'priority': 0.04,
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'audiolibrary.Config_Utility'>,
	 <class 'mpre.vmlibrary.Process'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **run**(self):

		No documentation available


- **write_config_file**(self, device_list):

		No documentation available


- **print_display_devices**(self, device_dict):

		No documentation available


- **get_selections**(self):

		No documentation available


Instruction
--------------

	 usage: Instruction(component_name, method_name, 
                           *args, **kwargs).execute(priority=priority)
                           
        Creates and executes an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds. 
        
        Instructions may be saved as an attribute of a component instead
        of continuously being instantiated. This allows the reuse of
        instruction objects. The same instruction object can be executed 
        any number of times.
        
        Note that Instructions must be executed to have any effect, and
        that they do not happen inline even if the priority is 0.0. In
        order to access the result of the executed function, a callback
        function can be provided.


Method resolution order: 

	(<class 'mpre.Instruction'>, <type 'object'>)

- **execute**(self, priority, callback, host_info, transport_protocol):

		 usage: instruction.execute(priority=0.0, callback=None)
        
            Submits an instruction to the processing queue. The instruction
            will be executed in priority seconds. An optional callback function 
            can be provided if the return value of the instruction is needed.


Latency
--------------

	 usage: Latency([name="component_name"], 
                       [average_size=20]) => latency_object
                       
        Latency objects possess a latency attribute that marks
        the average time between calls to latency.update()


Method resolution order: 

	(<class 'mpre.utilities.Latency'>, <type 'object'>)

- **update**(self):

		 usage: latency.update()
        
            notes the current time and adds it to the average time.


- **display**(self, mode):

		 usage: latency.display([mode='sys.stdin'])
        
            Writes latency information via either sys.stdin.write or print.
            Information includes the latency average, meta average, and max value


Wav_File
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'channels': 2,
	 'filename': '',
	 'mode': 'rb',
	 'rate': 48000,
	 'repeat': False,
	 'replace_reference_on_load': True,
	 'sample_width': 2,
	 'source_name': '',
	 'verbosity': ''}

Method resolution order: 

	(<class 'audiolibrary.Wav_File'>,
	 <class 'audiolibrary.Audio_Reactor'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **handle_audio_input**(self, sender, audio_data):

		No documentation available


- **write**(self, data):

		No documentation available


- **read**(self, size):

		No documentation available


- **close**(self):

		No documentation available


- **tell**(self):

		No documentation available
