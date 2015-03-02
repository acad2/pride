mpre.audio.audiolibrary
========
No documentation available

Audio_Channel
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- memory_size              65535
- audio_data               
- deleted                  False
- verbosity                

This object defines the following non-private methods:


- **read**(self, bytes=0):

		  No documentation available



- **handle_audio**(self, sender, audio):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.audiolibrary.Audio_Channel', class 'mpre.base.Base', type 'object')


Audio_Configuration_Utility
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- priority                 0.04
- memory_size              4096
- mode                     ('input',)
- auto_start               False
- config_file_name         audiocfg
- deleted                  False
- verbosity                

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **write_config_file**(self, device_list):

		  No documentation available



- **print_display_devices**(self, device_dict):

		  No documentation available



- **get_selections**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.audiolibrary.Audio_Configuration_Utility', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Audio_Device
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- frames_per_buffer        1024
- data_source              
- source_name              
- format                   8
- deleted                  False
- data                     
- verbosity                
- record_to_disk           False
- memory_size              16384
- frame_count              0

This object defines the following non-private methods:


- **handle_audio**(self, sender, packet):

		  No documentation available



- **open_stream**(self):

		  No documentation available



- **add_listener**(self, sender, packet):

		  No documentation available



- **get_data**(self):

		  No documentation available



- **handle_data**(self, audio_data):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.portaudiodevices.Audio_Device', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Audio_Input
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- frames_per_buffer        1024
- data_source              
- source_name              
- format                   8
- deleted                  False
- frame_count              0
- verbosity                
- record_to_disk           False
- memory_size              16384
- input                    True
- _data                    
- data                     

This object defines the following non-private methods:


- **get_data**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.portaudiodevices.Audio_Input', class 'mpre.audio.portaudiodevices.Audio_Device', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Audio_Manager
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- priority                 0.01
- memory_size              4096
- use_defaults             True
- auto_start               True
- config_file_name         
- deleted                  False
- verbosity                

This object defines the following non-private methods:


- **load_default_devices**(self):

		  No documentation available



- **run**(self):

		  No documentation available



- **send_channel_info**(self, sender, packet):

		  usage: Instruction("Audio_Manager", "send_channel_info", my_object).execute()
		 => Message: "Device_Info;;" + pickled list containing dictionaries
		 
		 Request a listing of available audio channels to the specified instances
		 memory. This message can be retrieved via instance.read_messages()



- **record**(self, device_name, file, channels=2, rate=48000):

		  No documentation available



- **play_file**(self, file, to=None, mute=False):

		  No documentation available



- **load_config_file**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.audiolibrary.Audio_Manager', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Audio_Output
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- frames_per_buffer        1024
- data_source              
- source_name              
- format                   8
- deleted                  False
- frame_count              0
- verbosity                
- mute                     False
- record_to_disk           False
- memory_size              16384
- output                   True
- data                     

This object defines the following non-private methods:


- **handle_audio**(self, sender, packet):

		  No documentation available



- **write_audio**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.portaudiodevices.Audio_Output', class 'mpre.audio.portaudiodevices.Audio_Device', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Audio_Service
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- deleted                  False
- verbosity                
- memory_size              65535

This object defines the following non-private methods:


- **handle_channel_info**(self, sender, packet):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.audiolibrary.Audio_Service', class 'mpre.base.Base', type 'object')


Instruction
--------
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
        that they do not happen inline, even if priority is 0.0. 
        Because they do not execute in the current scope, the return value 
        from the method call is not available through this mechanism.

Latency
--------
No documentation available

Wav_File
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- repeat                   False
- deleted                  False
- verbosity                
- filename                 
- channels                 2
- rate                     48000
- memory_size              4096
- mode                     rb
- sample_width             2

This object defines the following non-private methods:


- **write**(self, data):

		  No documentation available



- **read**(self, size=0):

		  No documentation available



- **close**(self):

		  No documentation available



- **tell**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.audiolibrary.Wav_File', class 'mpre.base.Base', type 'object')
