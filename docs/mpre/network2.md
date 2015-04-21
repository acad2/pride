mpre.network2
========
No documentation available

Authenticated_Client
--------
	No docstring found

Default values for newly created instances:

- username                 : 
- target                   : Authenticated_Service
- memory_mode              : -1
- deleted                  : False
- verbosity                : 
- memory_size              : 4096
- password                 : 
- email                    : 

This object defines the following non-private methods:


- **login_result**(self, sender, packet):

		  No documentation available



- **register**(self, sender, packet):

		  No documentation available



- **register_results**(self, sender, packet):

		  No documentation available



- **login**(self, sender=None, packet=None):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Authenticated_Client', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Authenticated_Service
--------
	No docstring found

Default values for newly created instances:

- database_filename        : :memory:
- memory_size              : 4096
- memory_mode              : -1
- deleted                  : False
- verbosity                : 
- hash_rounds              : 100000
- login_message            : login success

This object defines the following non-private methods:


- **on_load**(self, attributes):

		  No documentation available



- **register**(self, sender, packet):

		  No documentation available



- **logout**(self, sender, packet):

		  No documentation available



- **login**(self, sender, packet):

		  No documentation available



- **modify_user**(instance, sender, packet):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Authenticated_Service', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Download
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      : 16384
- memory_mode              : -1
- timeout_after            : 15
- deleted                  : False
- filename_prefix          : Download
- verbosity                : 
- filename                 : 
- memory_size              : 4096
- filesize                 : 0
- download_in_progress     : False

This object defines the following non-private methods:


- **record_data**(self, sender, data):

		  No documentation available



- **set_filesize**(self, sender, value):

		  No documentation available



- **make_request**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Download', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


File_Service
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      : 16384
- memory_size              : 4096
- memory_mode              : -1
- timeout_after            : 15
- deleted                  : False
- verbosity                : 
- mmap_threshold           : 16384

This object defines the following non-private methods:


- **get_filesize**(self, sender, filename):

		  No documentation available



- **slice_request**(self, sender, slice_info):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.File_Service', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


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
        that they do not happen inline even if the priority is 0.0. In
        order to access the result of the executed function, a callback
        function can be provided.

Latency
--------
 usage: Latency([name="component_name"], 
                       [average_size=20]) => latency_object
                       
        Latency objects possess a latency attribute that marks
        the average time between calls to latency.update()

Network_Service
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      : 32768
- added_to_network         : False
- memory_mode              : -1
- deleted                  : False
- verbosity                : 
- bind_on_init             : True
- _connecting              : False
- add_on_init              : True
- memory_size              : 0
- network_buffer           : 
- timeout                  : 0
- blocking                 : 0
- interface                : 0.0.0.0
- port                     : 0
- closed                   : False

This object defines the following non-private methods:


- **invalid_request**(self, sender, packet):

		  No documentation available



- **socket_recv**(self):

		  No documentation available



- **send_data**(self, data, to=None, response_to='None', expect_response=True):

		  No documentation available



- **demo_reaction**(self, sender, packet):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Network_Service', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Service_Listing
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      : 32768
- added_to_network         : False
- memory_mode              : -1
- deleted                  : False
- verbosity                : 
- bind_on_init             : True
- _connecting              : False
- add_on_init              : True
- port                     : 0
- memory_size              : 0
- network_buffer           : 
- timeout                  : 0
- interface                : 0.0.0.0
- blocking                 : 0
- closed                   : False

This object defines the following non-private methods:


- **send_listing**(self, sender, packet):

		  No documentation available



- **remove_service**(self, sender, packet):

		  No documentation available



- **set_service**(self, sender, packet):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Service_Listing', class 'mpre.network2.Network_Service', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Tcp_Client_Proxy
--------
	No docstring found

Default values for newly created instances:

- as_port                  : 0
- closed                   : False
- memory_mode              : -1
- deleted                  : False
- ip                       : 
- add_on_init              : True
- memory_size              : 0
- socket_family            : 2
- port                     : 80
- connection_attempts      : 10
- target                   : ()
- network_packet_size      : 32768
- timeout_notify           : True
- added_to_network         : False
- verbosity                : 
- bind_on_init             : False
- socket_type              : 1
- _connecting              : False
- blocking                 : 0
- bad_target_verbosity     : 0
- auto_connect             : True
- network_buffer           : 
- timeout                  : 0

This object defines the following non-private methods:


- **reply**(self, sender, packet):

		  No documentation available



- **recv**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Tcp_Client_Proxy', class 'mpre.network.Tcp_Client', class 'mpre.network.Tcp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Tcp_Service_Proxy
--------
	No docstring found

Default values for newly created instances:

- reuse_port               : 0
- closed                   : False
- memory_mode              : -1
- Tcp_Socket_type          : network.Tcp_Socket
- deleted                  : False
- add_on_init              : True
- memory_size              : 0
- interface                : 0.0.0.0
- socket_family            : 2
- port                     : 80
- connection_attempts      : 10
- name                     : 
- network_packet_size      : 32768
- added_to_network         : False
- verbosity                : 
- share_methods            : ('on_connect', 'client_socket_recv', 'client_socket_send')
- bind_on_init             : False
- socket_type              : 1
- _connecting              : False
- blocking                 : 0
- network_buffer           : 
- timeout                  : 0
- backlog                  : 50

This object defines the following non-private methods:


- **on_connect**(self, connection):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Tcp_Service_Proxy', class 'mpre.network.Server', class 'mpre.network.Tcp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Tcp_Service_Test
--------
	No docstring found

Default values for newly created instances:

- as_port                  : 0
- closed                   : False
- memory_mode              : -1
- deleted                  : False
- ip                       : 
- add_on_init              : True
- memory_size              : 0
- socket_family            : 2
- port                     : 80
- connection_attempts      : 10
- target                   : ()
- network_packet_size      : 32768
- timeout_notify           : True
- added_to_network         : False
- verbosity                : 
- bind_on_init             : False
- socket_type              : 1
- _connecting              : False
- blocking                 : 0
- bad_target_verbosity     : 0
- auto_connect             : True
- network_buffer           : 
- timeout                  : 0

This object defines the following non-private methods:


- **on_connect**(self):

		  No documentation available



- **recv**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network2.Tcp_Service_Test', class 'mpre.network.Tcp_Client', class 'mpre.network.Tcp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')
