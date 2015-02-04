mpre.networklibrary
========
No documentation available

Asynchronous_Network
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- keyboard_input           
- update_priority          5
- deleted                  False
- verbosity                
- number_of_sockets        0
- priority                 0.01
- memory_size              4096
- network_buffer           
- auto_start               True

This object defines the following non-private methods:


- **handle_writes**(self, writable_sockets):

		  No documentation available



- **run**(self):

		  No documentation available



- **handle_errors**(self, socket_list):

		  No documentation available



- **debuffer_data**(self, connection):

		  No documentation available



- **add_service**(self, address, service=''):

		  No documentation available



- **buffer_data**(self, connection, data, to=None):

		  No documentation available



- **handle_reads**(self, readable_sockets):

		  No documentation available



- **remove_service**(self, address):

		  No documentation available


This objects method resolution order is:

(class 'mpre.networklibrary.Asynchronous_Network', class 'mpre.vmlibrary.Process', class 'mpre.base.Base', type 'object')


Average
--------
No documentation available

Basic_Authentication
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- memory_size              4096
- deleted                  False
- verbosity                
- invalid_username_string  Invalid Username
- invalid_password_string  Invalid Password

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **handle_invalid_username**(self, connection):

		  No documentation available



- **handle_success**(self, connection):

		  No documentation available



- **handle_invalid_password**(self, connection):

		  No documentation available



- **delete**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.networklibrary.Basic_Authentication', class 'mpre.vmlibrary.Thread', class 'mpre.base.Base', type 'object')


Basic_Authentication_Client
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- memory_size              4096
- deleted                  False
- credentials              ()
- verbosity                

This object defines the following non-private methods:


- **retry**(self):

		  No documentation available



- **run**(self):

		  No documentation available



- **handle_invalid_username**(self):

		  No documentation available



- **handle_success**(self, connection):

		  No documentation available



- **handle_invalid_password**(self):

		  No documentation available



- **wait**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.networklibrary.Basic_Authentication_Client', class 'mpre.vmlibrary.Thread', class 'mpre.base.Base', type 'object')


Connection
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- timeout_after            0
- deleted                  False
- verbosity                
- socket_type              1
- add_on_init              True
- idle                     True
- allow_port_zero          True
- memory_size              0
- timeout                  0
- socket_family            2
- blocking                 0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.networklibrary.Connection', class 'mpre.networklibrary.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Connection_Manager
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- deleted                  False
- verbosity                
- memory_size              4096

This object defines the following non-private methods:


- **run**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.networklibrary.Connection_Manager', class 'mpre.vmlibrary.Thread', class 'mpre.base.Base', type 'object')


Inbound_Connection
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- timeout_after            0
- deleted                  False
- verbosity                
- socket_type              1
- add_on_init              True
- idle                     True
- allow_port_zero          True
- memory_size              0
- timeout                  0
- socket_family            2
- blocking                 0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.networklibrary.Inbound_Connection', class 'mpre.networklibrary.Connection', class 'mpre.networklibrary.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Instruction
--------
No documentation available

Latency
--------
No documentation available

Multicast_Beacon
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- packet_ttl               
- timeout_after            0
- deleted                  False
- verbosity                
- add_on_init              True
- multicast_group          224.0.0.0
- idle                     True
- allow_port_zero          True
- memory_size              0
- timeout                  10
- blocking                 0
- interface                0.0.0.0
- multicast_port           1929
- port                     0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.networklibrary.Multicast_Beacon', class 'mpre.networklibrary.UDP_Socket', class 'mpre.networklibrary.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Multicast_Receiver
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- timeout_after            0
- deleted                  False
- ip                       224.0.0.0
- verbosity                
- add_on_init              True
- idle                     True
- allow_port_zero          True
- memory_size              0
- timeout                  10
- blocking                 0
- interface                0.0.0.0
- port                     0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.networklibrary.Multicast_Receiver', class 'mpre.networklibrary.UDP_Socket', class 'mpre.networklibrary.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Outbound_Connection
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- timeout_notify           True
- connect_attempts         10
- target                   ()
- timeout_after            0
- deleted                  False
- ip                       
- verbosity                
- as_port                  0
- socket_type              1
- add_on_init              False
- port                     80
- bad_target_verbosity     0
- idle                     True
- allow_port_zero          True
- memory_size              0
- timeout                  0
- socket_family            2
- blocking                 0

This object defines the following non-private methods:


- **attempt_connection**(self):

		  No documentation available



- **unhandled_error**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.networklibrary.Outbound_Connection', class 'mpre.networklibrary.Connection', class 'mpre.networklibrary.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Server
--------
	usage: Instruction("Asynchronous_Network", "create", "networklibrary.Server",
	socket_recv=mysocket_recv, socket_send=mysocket_send, on_connect=myonconnection,
	name="My_Server", port=40010).execute()

Default values for newly created instances:

- network_packet_size      4096
- reuse_port               0
- name                     
- timeout_after            0
- deleted                  False
- verbosity                
- share_methods            ('on_connect', 'client_socket_recv', 'client_socket_send')
- socket_type              1
- add_on_init              True
- port                     80
- idle                     True
- allow_port_zero          True
- memory_size              0
- timeout                  0
- interface                localhost
- inbound_connection_type  networklibrary.Inbound_Connection
- socket_family            2
- blocking                 0
- backlog                  50

This object defines the following non-private methods:


- **handle_bind_error**(self):

		  No documentation available



- **socket_recv**(self, server):

		  No documentation available


This objects method resolution order is:

(class 'mpre.networklibrary.Server', class 'mpre.networklibrary.Connection', class 'mpre.networklibrary.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Service_Listing
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

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **add_service**(self, address):

		  No documentation available



- **process_request**(self):

		  No documentation available



- **remove_local_service**(self, address):

		  No documentation available



- **add_local_service**(self, address, service_name):

		  No documentation available



- **remove_service**(self, address):

		  No documentation available


This objects method resolution order is:

(class 'mpre.networklibrary.Service_Listing', class 'mpre.vmlibrary.Process', class 'mpre.base.Base', type 'object')


Socket
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- timeout_after            0
- deleted                  False
- verbosity                
- add_on_init              True
- idle                     True
- allow_port_zero          True
- memory_size              0
- timeout                  0
- blocking                 0

This object defines the following non-private methods:


- **handle_idle**(self):

		  No documentation available



- **delete**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.networklibrary.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


UDP_Socket
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- timeout_after            0
- deleted                  False
- verbosity                
- add_on_init              True
- port                     0
- idle                     True
- allow_port_zero          True
- memory_size              0
- timeout                  10
- interface                0.0.0.0
- blocking                 0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.networklibrary.UDP_Socket', class 'mpre.networklibrary.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')
