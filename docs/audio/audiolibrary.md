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


- **run**(self):

		  No documentation available



- **read**(self, bytes=0):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.audiolibrary.Audio_Channel', class 'mpre.vmlibrary.Thread', class 'mpre.base.Base', type 'object')


Audio_Configuration_Utility
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- keyboard_input           
- deleted                  False
- verbosity                
- priority                 0.04
- memory_size              4096
- network_buffer           
- auto_start               False
- config_file_name         audiocfg
- mode                     ('input',)

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

(class 'mpre.audio.audiolibrary.Audio_Configuration_Utility', class 'mpre.vmlibrary.Process', class 'mpre.base.Base', type 'object')


Audio_Device
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- frames_per_buffer        1024
- format                   8
- deleted                  False
- frame_count              0
- verbosity                
- record_to_disk           False
- memory_size              65535
- data                     

This object defines the following non-private methods:


- **get_data**(self):

		  No documentation available



- **handle_data**(self, audio_data):

		  No documentation available



- **open_stream**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.portaudiodevices.Audio_Device', class 'mpre.vmlibrary.Thread', class 'mpre.base.Base', type 'object')


Audio_Input
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- frames_per_buffer        1024
- format                   8
- deleted                  False
- data                     
- verbosity                
- record_to_disk           False
- memory_size              65535
- input                    True
- _data                    
- frame_count              0

This object defines the following non-private methods:


- **read**(self, size=0):

		  No documentation available



- **get_data**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.portaudiodevices.Audio_Input', class 'mpre.audio.portaudiodevices.Audio_Device', class 'mpre.vmlibrary.Thread', class 'mpre.base.Base', type 'object')


Audio_Manager
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- keyboard_input           
- use_defaults             True
- deleted                  False
- verbosity                
- priority                 0.01
- memory_size              4096
- network_buffer           
- auto_start               True
- config_file_name         audiocfg

This object defines the following non-private methods:


- **add_listener**(self, listener, device_name):

		  No documentation available



- **load_default_devices**(self):

		  No documentation available



- **run**(self):

		  No documentation available



- **send_channel_info**(self, listener):

		  usage: Instruction("Audio_Manager", "send_channel_info", my_object).execute()
		 => Message: "Device_Info;;" + pickled list containing dictionaries
		 
		 Request a listing of available audio channels to the specified instances
		 memory. This message can be retrieved via instance.read_messages()



- **record**(self, device_name, file, channels=2, rate=48000):

		  No documentation available



- **play_file**(self, file_info, file, to=None, mute=False):

		  No documentation available



- **load_config_file**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.audiolibrary.Audio_Manager', class 'mpre.vmlibrary.Process', class 'mpre.base.Base', type 'object')


Audio_Output
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- frames_per_buffer        1024
- data_source              None
- format                   8
- deleted                  False
- data                     
- verbosity                
- mute                     False
- record_to_disk           False
- memory_size              65535
- output                   True
- frame_count              0

This object defines the following non-private methods:


- **get_data**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.portaudiodevices.Audio_Output', class 'mpre.audio.portaudiodevices.Audio_Device', class 'mpre.vmlibrary.Thread', class 'mpre.base.Base', type 'object')


Audio_Service
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- deleted                  False
- verbosity                
- memory_size              65535

This object defines the following non-private methods:


- **run**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.audiolibrary.Audio_Service', class 'mpre.vmlibrary.Thread', class 'mpre.base.Base', type 'object')


Instruction
--------
No documentation available

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
