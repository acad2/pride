audiolibrary
==============



Audio_File
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'file': None,
	 'file_type': 'file',
	 'mode': '',
	 'persistent': True,
	 'replace_reference_on_load': True,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'audiolibrary.Audio_File'>,
	 <class 'mpre.fileio.File'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **handle_audio_input**(self, audio_data):

				No documentation available


Audio_Manager
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'config_file_name': '',
	 'configure': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'replace_reference_on_load': True,
	 'use_defaults': True}

Method resolution order: 

	(<class 'audiolibrary.Audio_Manager'>,
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
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'replace_reference_on_load': True,
	 'source_name': ''}

Method resolution order: 

	(<class 'audiolibrary.Audio_Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **add_listener**(self, instance_name):

				No documentation available


- **handle_audio_output**(self, audio_data):

				No documentation available


- **handle_audio_input**(self, audio_data):

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
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'mode': ('input',),
	 'priority': 0.04,
	 'replace_reference_on_load': True,
	 'run_callback': None,
	 'running': True}

Method resolution order: 

	(<class 'audiolibrary.Config_Utility'>,
	 <class 'mpre.vmlibrary.Process'>,
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
                           *args, **kwargs).execute(priority=priority,
                                                    callback=callback,
                                                    host_info=(ip, port))
                           
        Creates and executes an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        host_info may supply an ip address string and port number integer
        to execute the instruction on a remote machine. This requirements
        for this to be a success are:
            
            - The machine must have an instance of metapython running
            - The machine must be accessible via the network
            - The local machine must be registered and logged in to
              the remote machine
            - The local machine may need to be registered and logged in to
              have permission to the use the specific component and method
              in question
            - The local machine ip must not be blacklisted by the remote
              machine.
            - The remote machine may require that the local machine ip
              be in a whitelist to access the method in question.
              
        Other then the security requirements, remote procedure calls require 
        zero config on the part of either host. An object will be accessible
        if it exists on the machine in question.
              
        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed if the instruction is being executed
        locally. If the instruction is being executed remotely, this instead
        acts as a flag. If set to a True value, the instruction will be
        placed at the front of the local queue to be sent to the host.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds or sent to the machine in question. 
        
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

		 usage: instruction.execute(priority=0.0, callback=None,
                                       host_info=tuple())
        
            Submits an instruction to the processing queue. If being executed
            locally, the instruction will be executed in priority seconds. 
            An optional callback function can be provided if the return value 
            of the instruction is needed.
            
            host_info may be specified to designate a remote machine that
            the Instruction should be executed on. If being executed remotely, 
            priority is a high_priority flag where 0 means the instruction will
            be placed at the end of the rpc queue for the remote host in 
            question. If set, the instruction will instead be placed at the 
            beginning of the queue.
            
            Remotely executed instructions have a default callback, which is 
            the appropriate RPC_Requester.alert.
            
            The transport protocol flag is currently unused. Support for
            UDP and other protocols could be implemented and dispatched
            via this flag.


Latency
--------------

	 usage: Latency([name="component_name"], 
                       [size=20]) => latency_object
                       
        Latency objects possess a latency attribute that marks
        the average time between calls to latency.update()


Method resolution order: 

	(<class 'mpre.utilities.Latency'>, <type 'object'>)

- **finish_measuring**(self):

				No documentation available


- **start_measuring**(self):

				No documentation available


Wav_File
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'channels': 2,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'file': None,
	 'file_type': 'file',
	 'filename': '',
	 'mode': 'rb',
	 'persistent': True,
	 'rate': 48000,
	 'repeat': False,
	 'replace_reference_on_load': True,
	 'sample_width': 2,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'audiolibrary.Wav_File'>,
	 <class 'audiolibrary.Audio_File'>,
	 <class 'mpre.fileio.File'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **write**(self, data):

				No documentation available


- **read**(self, size):

				No documentation available


- **close**(self):

				No documentation available


- **tell**(self):

				No documentation available


record_wav_file
--------------

**record_wav_file**(parse_args, **kwargs):

				No documentation available
