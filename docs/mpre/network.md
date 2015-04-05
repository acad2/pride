mpre.network
========
No documentation available

Average
--------
 usage: Average([name=''], [size=20], 
                       [values=tuple()], [meta_average=False]) => average_object
                       
        Average objects keep a running average via the add method.
        The size option specifies the maximum number of samples. When
        this limit is reached, additional samples will result in the
        oldest sample being removed.
        
        values may be used to seed the average.
        
        The meta_average boolean flag is used to determine whether or not
        to keep an average of the average - This is implemented by an
        additional Average object.

Connection_Manager
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

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **add**(self, sock):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Connection_Manager', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Error_Handler
--------
No documentation available

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

Multicast_Beacon
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- packet_ttl               
- added_to_network         False
- memory_mode              -1
- deleted                  False
- verbosity                
- blocking                 0
- bind_on_init             True
- add_on_init              True
- multicast_group          224.0.0.0
- memory_size              0
- network_buffer           
- timeout                  0
- update_flag              False
- interface                0.0.0.0
- multicast_port           1929
- port                     0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.network.Multicast_Beacon', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Multicast_Receiver
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
- address                  224.0.0.0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.network.Multicast_Receiver', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Network
--------
	No docstring found

Default values for newly created instances:

- handle_resends           False
- memory_mode              -1
- deleted                  False
- verbosity                
- number_of_sockets        0
- priority                 0.01
- memory_size              4096
- auto_start               False
- update_flag              False
- update_priority          5

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **handle_delayed_sends**(self, writable):

		  No documentation available



- **send**(self, sock, data):

		  No documentation available



- **remove**(self, sock):

		  No documentation available



- **handle_reads**(self, readable_sockets):

		  No documentation available



- **add**(self, sock):

		  No documentation available



- **sendto**(self, sock, data, host_info):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Network', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Server
--------
	No docstring found

Default values for newly created instances:

- reuse_port               0
- memory_mode              -1
- Tcp_Socket_type          network.Tcp_Socket
- deleted                  False
- add_on_init              True
- memory_size              0
- interface                0.0.0.0
- socket_family            2
- port                     80
- name                     
- network_packet_size      32768
- added_to_network         False
- verbosity                
- share_methods            ('on_connect', 'client_socket_recv', 'client_socket_send')
- bind_on_init             False
- socket_type              1
- blocking                 0
- network_buffer           
- timeout                  0
- update_flag              False
- backlog                  50

This object defines the following non-private methods:


- **on_connect**(self, connection):

		  No documentation available



- **handle_bind_error**(self):

		  No documentation available



- **recv**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Server', class 'mpre.network.Tcp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Socket
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- added_to_network         False
- memory_mode              -1
- deleted                  False
- verbosity                
- bind_on_init             False
- blocking                 0
- memory_size              0
- network_buffer           
- timeout                  0
- update_flag              False
- interface                0.0.0.0
- add_on_init              True
- port                     0

This object defines the following non-private methods:


- **send**(self, data):

		  No documentation available



- **recvfrom**(self, buffer_size=0):

		  No documentation available



- **sendto**(self, data, host_info):

		  No documentation available



- **close**(self):

		  No documentation available



- **recv**(self, buffer_size=0):

		  No documentation available



- **delete**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Tcp_Client
--------
	No docstring found

Default values for newly created instances:

- as_port                  0
- memory_mode              -1
- deleted                  False
- ip                       
- add_on_init              False
- memory_size              0
- socket_family            2
- port                     80
- target                   ()
- network_packet_size      32768
- timeout_notify           True
- connect_attempts         10
- added_to_network         False
- verbosity                
- bind_on_init             False
- socket_type              1
- blocking                 0
- bad_target_verbosity     0
- network_buffer           
- timeout                  0
- update_flag              False

This object defines the following non-private methods:


- **attempt_connection**(self):

		  No documentation available



- **on_connect**(self):

		  No documentation available



- **unhandled_error**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Tcp_Client', class 'mpre.network.Tcp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Tcp_Socket
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- added_to_network         False
- memory_mode              -1
- deleted                  False
- verbosity                
- bind_on_init             False
- socket_type              1
- add_on_init              True
- port                     0
- memory_size              0
- network_buffer           
- timeout                  0
- update_flag              False
- interface                0.0.0.0
- socket_family            2
- blocking                 0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.network.Tcp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Udp_Socket
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- added_to_network         False
- memory_mode              -1
- deleted                  False
- verbosity                
- bind_on_init             True
- add_on_init              True
- port                     0
- memory_size              0
- network_buffer           
- timeout                  0
- update_flag              False
- interface                0.0.0.0
- blocking                 0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')
