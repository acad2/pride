mpre.network2
========
No documentation available

Authenticated_Client
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- username                 
- timeout_after            0
- deleted                  False
- resend_limit             10
- verbosity                
- add_on_init              True
- resend_interval          0.2
- email                    
- idle                     True
- allow_port_zero          True
- memory_size              32768
- network_buffer           
- timeout                  0
- blocking                 0
- interface                0.0.0.0
- password                 
- port                     0

This object defines the following non-private methods:


- **login_result**(self, sender, packet):

		  No documentation available



- **register**(self, sender, packet):

		  No documentation available



- **login**(self, sender, packet):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Authenticated_Client', class 'mpre.network2.Service', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Authenticated_Service
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- database_filename        :memory:
- copyright                Type "help", "copyright", "credits" or "license" for more information.
- timeout_after            0
- deleted                  False
- resend_limit             10
- verbosity                
- add_on_init              True
- resend_interval          0.2
- idle                     True
- allow_port_zero          True
- memory_size              32768
- network_buffer           
- timeout                  0
- blocking                 0
- interface                0.0.0.0
- login_message            login success
- port                     40022

This object defines the following non-private methods:


- **register**(self, sender, packet):

		  No documentation available



- **logout**(self, sender, packet):

		  No documentation available



- **login**(self, sender, packet):

		  No documentation available



- **modify_user**(instance, sender, packet):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Authenticated_Service', class 'mpre.network2.Service', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Download
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      16384
- filename_prefix          Download
- timeout_after            15
- deleted                  False
- resend_limit             10
- verbosity                
- add_on_init              True
- resend_interval          0.2
- download_in_progress     False
- idle                     True
- allow_port_zero          True
- memory_size              32768
- network_buffer           
- timeout                  0
- blocking                 0
- interface                0.0.0.0
- filename                 
- port                     0
- filesize                 0

This object defines the following non-private methods:


- **record_data**(self, sender, data):

		  No documentation available



- **set_filesize**(self, sender, value):

		  No documentation available



- **make_request**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Download', class 'mpre.network2.Service', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


File_Service
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      16384
- timeout_after            15
- deleted                  False
- resend_limit             10
- verbosity                
- mmap_threshold           16384
- add_on_init              True
- resend_interval          0.2
- idle                     True
- allow_port_zero          True
- memory_size              32768
- network_buffer           
- timeout                  0
- blocking                 0
- interface                0.0.0.0
- port                     0

This object defines the following non-private methods:


- **slice_request**(self, sender, slice_info):

		  No documentation available



- **get_filesize**(self, sender, filename):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.File_Service', class 'mpre.network2.Service', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Instruction
--------
No documentation available

Latency
--------
No documentation available

Service
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- resend_interval          0.2
- timeout_after            0
- deleted                  False
- resend_limit             10
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


- **read_messages**(self):

		  No documentation available



- **invalid_request**(self, sender, packet):

		  No documentation available



- **socket_recv**(self):

		  No documentation available



- **make_packet**(self, response_to, data):

		  No documentation available



- **react**(self):

		  No documentation available



- **rpc**(self, target, data, response_to='None', expect_response=True, local=False):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Service', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Service_Listing
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- timeout_after            0
- deleted                  False
- resend_limit             10
- verbosity                
- add_on_init              True
- resend_interval          0.2
- idle                     True
- allow_port_zero          True
- memory_size              32768
- network_buffer           
- timeout                  0
- blocking                 0
- interface                0.0.0.0
- port                     0

This object defines the following non-private methods:


- **send_listing**(self, sender, packet):

		  No documentation available



- **remove_service**(self, sender, packet):

		  No documentation available



- **set_service**(self, sender, packet):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Service_Listing', class 'mpre.network2.Service', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Tcp_Client_Proxy
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- timeout_after            0
- deleted                  False
- verbosity                
- socket_type              1
- add_on_init              True
- idle                     True
- allow_port_zero          True
- memory_size              32768
- network_buffer           
- timeout                  0
- blocking                 0
- interface                0.0.0.0
- socket_family            2
- port                     0

This object defines the following non-private methods:


- **socket_recv**(self):

		  No documentation available



- **reply**(self, sender, packet):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Tcp_Client_Proxy', class 'mpre.network.Inbound_Connection', class 'mpre.network.Connection', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Tcp_Service_Proxy
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- reuse_port               0
- name                     
- timeout_after            0
- deleted                  False
- verbosity                
- share_methods            ('on_connect', 'client_socket_recv', 'client_socket_send')
- socket_type              1
- add_on_init              True
- idle                     True
- allow_port_zero          True
- memory_size              32768
- network_buffer           
- timeout                  0
- blocking                 0
- interface                0.0.0.0
- inbound_connection_type  network.Inbound_Connection
- socket_family            2
- port                     80
- backlog                  50

This object defines the following non-private methods:


- **on_connect**(self, connection):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Tcp_Service_Proxy', class 'mpre.network.Server', class 'mpre.network.Connection', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Tcp_Service_Test
--------
	No docstring found

Default values for newly created instances:

- as_port                  0
- deleted                  False
- ip                       
- add_on_init              False
- allow_port_zero          True
- memory_size              32768
- socket_family            2
- blocking                 0
- network_packet_size      32768
- timeout_notify           True
- connect_attempts         10
- target                   ()
- timeout_after            0
- verbosity                
- socket_type              1
- port                     80
- bad_target_verbosity     0
- idle                     True
- network_buffer           
- timeout                  0

This object defines the following non-private methods:


- **socket_recv**(self):

		  No documentation available



- **on_connect**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Tcp_Service_Test', class 'mpre.network.Outbound_Connection', class 'mpre.network.Connection', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')
