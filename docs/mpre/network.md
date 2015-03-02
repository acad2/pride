mpre.network
========
No documentation available

Asynchronous_Network
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- handle_resends           False
- deleted                  False
- verbosity                
- number_of_sockets        0
- priority                 0.01
- memory_size              4096
- auto_start               False
- update_priority          5

This object defines the following non-private methods:


- **debuffer_data**(self, connection):

		  No documentation available



- **run**(self):

		  No documentation available



- **send**(self, sock, data, to=None):

		  No documentation available



- **handle_reads**(self, readable_sockets):

		  No documentation available



- **add**(self, sock):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Asynchronous_Network', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Average
--------
No documentation available

Connection
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- timeout_after            0
- deleted                  False
- verbosity                
- socket_type              1
- add_on_init              True
- port                     0
- idle                     True
- allow_port_zero          True
- memory_size              32768
- network_buffer           
- timeout                  0
- interface                0.0.0.0
- socket_family            2
- blocking                 0

This object defines the following non-private methods:


- **socket_recv**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Connection', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Connection_Manager
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- priority                 0.04
- memory_size              4096
- auto_start               False
- deleted                  False
- verbosity                

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **add**(self, sock):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Connection_Manager', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Inbound_Connection
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

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.network.Inbound_Connection', class 'mpre.network.Connection', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


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
No documentation available

Multicast_Beacon
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

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.network.Multicast_Beacon', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Multicast_Receiver
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- timeout_after            0
- deleted                  False
- ip                       224.0.0.0
- verbosity                
- add_on_init              True
- idle                     True
- allow_port_zero          True
- memory_size              32768
- network_buffer           
- timeout                  0
- blocking                 0
- interface                0.0.0.0
- port                     0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.network.Multicast_Receiver', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Outbound_Connection
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


- **attempt_connection**(self):

		  No documentation available



- **unhandled_error**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Outbound_Connection', class 'mpre.network.Connection', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Server
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


- **handle_bind_error**(self):

		  No documentation available



- **socket_recv**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Server', class 'mpre.network.Connection', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Socket
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- timeout                  0
- timeout_after            0
- deleted                  False
- verbosity                
- add_on_init              True
- idle                     True
- allow_port_zero          True
- memory_size              32768
- network_buffer           
- blocking                 0
- interface                0.0.0.0
- port                     0

This object defines the following non-private methods:


- **socket_recv**(self):

		  No documentation available



- **send_data**(self, data, to=None):

		  No documentation available



- **delete**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Udp_Socket
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

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')
