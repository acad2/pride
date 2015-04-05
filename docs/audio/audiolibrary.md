mpre.audio.audiolibrary
========
No documentation available

Audio_File
--------
	No docstring found

Default values for newly created instances:

- memory_size              4096
- memory_mode              -1
- update_flag              False
- deleted                  False
- verbosity                
- storage_mode             dont_copy

This object defines the following non-private methods:


- **handle_audio_input**(self, sender, audio_data):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.audiolibrary.Audio_File', class 'mpre.fileio.File', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Audio_Manager
--------
	No docstring found

Default values for newly created instances:

- configure                False
- memory_mode              -1
- deleted                  False
- verbosity                
- config_file_name         
- memory_size              4096
- update_flag              False
- use_defaults             True

This object defines the following non-private methods:


- **load_api**(self):

		  No documentation available



- **load_default_devices**(self):

		  No documentation available



- **record**(self, device_name, file, channels=2, rate=48000):

		  No documentation available



- **run_configuration**(self, exit_when_finished=False):

		  No documentation available



- **load_config_file**(self):

		  No documentation available



- **get_devices**(self, devices='Audio_Input'):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.audiolibrary.Audio_Manager', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Audio_Reactor
--------
	No docstring found

Default values for newly created instances:

- memory_size              4096
- memory_mode              -1
- update_flag              False
- deleted                  False
- source_name              
- verbosity                

This object defines the following non-private methods:


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


This objects method resolution order is:

(class 'mpre.audio.audiolibrary.Audio_Reactor', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Config_Utility
--------
	No docstring found

Default values for newly created instances:

- priority                 0.04
- memory_size              4096
- memory_mode              -1
- auto_start               False
- update_flag              False
- deleted                  False
- verbosity                
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

(class 'mpre.audio.audiolibrary.Config_Utility', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


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
 usage: Latency([name="component_name"], 
                       [average_size=20]) => latency_object
                       
        Latency objects possess a latency attribute that marks
        the average time between calls to latency.update()

Wav_File
--------
	No docstring found

Default values for newly created instances:

- repeat                   False
- source_name              
- memory_mode              -1
- deleted                  False
- verbosity                
- filename                 
- channels                 2
- rate                     48000
- memory_size              4096
- mode                     rb
- update_flag              False
- sample_width             2

This object defines the following non-private methods:


- **handle_audio_input**(self, sender, audio_data):

		  No documentation available



- **write**(self, data):

		  No documentation available



- **read**(self, size=None):

		  No documentation available



- **close**(self):

		  No documentation available



- **tell**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.audiolibrary.Wav_File', class 'mpre.audio.audiolibrary.Audio_Reactor', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')
