mpre.audiofli2
========
No documentation available

Audiofli_Server
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- added_to_network         False
- memory_mode              -1
- timeout_after            20
- deleted                  False
- verbosity                
- blocking                 0
- bind_on_init             True
- add_on_init              True
- memory_size              0
- network_buffer           
- timeout                  0
- update_flag              False
- interface                0.0.0.0
- port                     8001

This object defines the following non-private methods:


- **handle_audio_input**(self, sender, audio_data):

		  No documentation available



- **handle_dropouts**(self):

		  No documentation available



- **set_input_device**(self, instance_name):

		  No documentation available



- **recvfrom**(self):

		  No documentation available



- **half_sample**(self, audio_data):

		  No documentation available



- **handle_connection_reset**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audiofli2.Audiofli_Server', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Channel_Broadcaster
--------
	No docstring found

Default values for newly created instances:

- memory_mode              -1
- deleted                  False
- add_on_init              True
- running                  True
- memory_size              0
- interface                0.0.0.0
- multicast_port           1929
- blocking                 0
- network_packet_size      32768
- packet_ttl               
- added_to_network         False
- verbosity                
- bind_on_init             True
- port                     0
- multicast_group          239.192.12.47
- network_buffer           
- timeout                  0
- update_flag              False
- host_name                192.168.1.230

This object defines the following non-private methods:


- **create_beacon_message**(self, channel, ip, port):

		  No documentation available



- **send_beacon**(self, channel):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audiofli2.Channel_Broadcaster', class 'mpre.network.Multicast_Beacon', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


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