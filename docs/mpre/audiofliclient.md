mpre.audiofliclient
========
No documentation available

Audiofli_Client
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- added_to_network         False
- memory_mode              -1
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
- port                     0

This object defines the following non-private methods:


- **ping**(self, address):

		  No documentation available



- **recvfrom**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audiofliclient.Audiofli_Client', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Beacon_Listener
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- added_to_network         False
- memory_mode              -1
- deleted                  False
- verbosity                
- address                  239.192.12.47
- bind_on_init             True
- add_on_init              True
- port                     1929
- memory_size              0
- network_buffer           
- timeout                  0
- update_flag              False
- interface                0.0.0.0
- blocking                 0

This object defines the following non-private methods:


- **stop_stream**(self):

		  No documentation available



- **recvfrom**(self):

		  No documentation available



- **select_channel**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audiofliclient.Beacon_Listener', class 'mpre.network.Multicast_Receiver', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')
