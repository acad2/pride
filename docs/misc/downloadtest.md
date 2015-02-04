mpre.misc.downloadtest
========
No documentation available

Download
--------
	No docstring found

Default values for newly created instances:

- filename                 
- deleted                  False
- ip                       
- add_on_init              False
- allow_port_zero          True
- memory_size              0
- blocking                 0
- connect_attempts         10
- socket_family            2
- as_port                  0
- network_packet_size      16384
- timeout_notify           True
- target                   ()
- timeout_after            15
- filename_prefix          Download
- verbosity                
- socket_type              1
- port                     40021
- bad_target_verbosity     0
- idle                     True
- filesize                 0
- timeout                  0
- download_in_progress     False

This object defines the following non-private methods:


- **handle_response**(self, packet):

		  No documentation available



- **socket_recv**(self, connection):

		  No documentation available



- **socket_send**(self, connection, data):

		  No documentation available



- **record_response**(self, response):

		  No documentation available



- **make_request**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.misc.downloadtest.Download', class 'mpre.networklibrary.UDP_Socket', class 'mpre.networklibrary.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


File_Server
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      16384
- use_mmap                 False
- file                     
- mmap_file                False
- filename                 
- timeout_after            15
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

This object defines the following non-private methods:


- **socket_recv**(self, connection):

		  No documentation available



- **socket_send**(self, connection, data, to):

		  No documentation available



- **handle_request**(self, request, address):

		  No documentation available



- **make_response**(self, filename, start_from, request_size):

		  No documentation available


This objects method resolution order is:

(class 'mpre.misc.downloadtest.File_Server', class 'mpre.networklibrary.UDP_Socket', class 'mpre.networklibrary.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


File_Service
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      16384
- keyboard_input           
- asynchronous_server      True
- deleted                  False
- verbosity                
- priority                 0.04
- memory_size              4096
- network_buffer           
- auto_start               False
- interface                0.0.0.0
- port                     40021

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.misc.downloadtest.File_Service', class 'mpre.networklibrary.UDP_Socket', class 'mpre.networklibrary.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Instruction
--------
No documentation available