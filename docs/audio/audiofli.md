mpre.audio.audiofli
========
No documentation available

Audio_Server
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- timeout_after            0
- deleted                  False
- verbosity                
- add_on_init              True
- port                     0
- idle                     True
- allow_port_zero          True
- memory_size              32768
- network_buffer           
- timeout                  0
- interface                0.0.0.0
- blocking                 0

This object defines the following non-private methods:


- **socket_recv**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.audiofli.Audio_Server', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Audiofli_Server
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- priority                 0.04
- memory_size              4096
- auto_start               True
- deleted                  False
- verbosity                

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **make_header**(self, device, channels=1, ios=False):

		  No documentation available



- **create_channel_beacons**(self):

		  No documentation available



- **parse_command**(self, message):

		  No documentation available



- **create_audio_server**(self):

		  No documentation available



- **record_data**(self, audio_data):

		  No documentation available



- **half_sample**(self, audio_data):

		  No documentation available



- **handle_command**(self, data, _socket, _from):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.audiofli.Audiofli_Server', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Channel_Broadcaster
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- packet_ttl               
- timeout_after            0
- deleted                  False
- verbosity                
- add_on_init              True
- multicast_group          224.0.0.0
- idle                     True
- allow_port_zero          True
- memory_size              32768
- network_buffer           
- timeout                  0
- blocking                 0
- interface                0.0.0.0
- multicast_port           1929
- port                     0

This object defines the following non-private methods:


- **create_beacon_message**(self, channel, ip, port):

		  No documentation available



- **send_beacon**(self, channel):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.audiofli.Channel_Broadcaster', class 'mpre.network.Multicast_Beacon', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Instruction
--------
 usage: Instruction(component_name, method_name, 
                           *args, **kwargs) => instruction_object
                           
        Creates an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        Instruction objects have a priority attribute. This attribute
        defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds. 
        
        Instructions may be saved as an attribute of a component instead
        of continuously being instantiated. This allows the reuse of
        instruction objects. 
        
        Note that Instructions must be executed to have any effect, and
        that they do not happen inline, even if priority is 0.0. 
        Because they do not execute in the current scope, the return value 
        from the method call is not available through this mechanism.

Latency
--------
No documentation available