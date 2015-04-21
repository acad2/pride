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
        that they do not happen inline even if the priority is 0.0. In
        order to access the result of the executed function, a callback
        function can be provided.

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

- network_packet_size      : 32768
- packet_ttl               : 
- added_to_network         : False
- memory_mode              : -1
- deleted                  : False
- verbosity                : 
- bind_on_init             : True
- _connecting              : False
- add_on_init              : True
- multicast_group          : 224.0.0.0
- memory_size              : 0
- network_buffer           : 
- timeout                  : 0
- blocking                 : 0
- interface                : 0.0.0.0
- multicast_port           : 1929
- port                     : 0
- closed                   : False

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.network.Multicast_Beacon', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Multicast_Receiver
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      : 32768
- added_to_network         : False
- memory_mode              : -1
- deleted                  : False
- verbosity                : 
- address                  : 224.0.0.0
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

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.network.Multicast_Receiver', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Network
--------
	 Manages socket objects and is responsible for calling select.select to determine
	readability/writability of sockets. Also responsible for non blocking connect logic. 
	This component is created by default upon application startup, and in most cases will
	not require user interaction.

Default values for newly created instances:

- handle_resends           : False
- memory_mode              : -1
- deleted                  : False
- verbosity                : 
- _updating                : False
- number_of_sockets        : 0
- priority                 : 0.01
- memory_size              : 4096
- auto_start               : False
- update_priority          : 5

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **remove**(self, sock):

		  No documentation available



- **is_writable**(self, sock):

		  No documentation available



- **add**(self, sock):

		  No documentation available



- **connect**(self, sock):

		  No documentation available



- **delete**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Network', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


NotWritableError
--------
No documentation available

Server
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

		  Connection logic that the server should apply when a new client has connected.
		 This method should be overloaded by subclasses



- **handle_bind_error**(self):

		  No documentation available



- **recv**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Server', class 'mpre.network.Tcp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Socket
--------
	 Provides a mostly transparent asynchronous socket interface by applying a 
	Wrapper to a _socketobject. The default socket family is socket.AF_INET and
	the default socket type is socket.SOCK_STREAM (a.k.a. a tcp socket).

Default values for newly created instances:

- closed                   : False
- memory_mode              : -1
- deleted                  : False
- add_on_init              : True
- memory_size              : 0
- interface                : 0.0.0.0
- port                     : 0
- connection_attempts      : 10
- network_packet_size      : 32768
- added_to_network         : False
- verbosity                : 
- bind_on_init             : False
- _connecting              : False
- blocking                 : 0
- network_buffer           : 
- timeout                  : 0

This object defines the following non-private methods:


- **sendto**(self, data, host_info):

		  Sends data via the underlying _socketobject to the specified address. The socket
		 is first checked to ensure writability before sending. If the socket is not
		 writable, NotWritableError is raised.



- **connect**(self, address):

		  Perform a non blocking connect to the specified address. The on_connect method
		 is called when the connection succeeds, or the appropriate error handler method
		 is called if the connection fails. Subclasses should overload on_connect instead
		 of this method.



- **close**(self):

		  No documentation available



- **recv**(self, buffer_size=0):

		  Receives data from a remote endpoint. This method is event triggered and called
		 when the socket becomes readable according to select.select. Subclasses should
		 extend this method to customize functionality for when data is received. This
		 method is called for Tcp sockets and requires a connection.



- **on_connect**(self):

		  Performs any logic required when a Tcp connection succeeds. This method should
		 be overloaded by subclasses.



- **send**(self, data):

		  Sends data via the underlying _socketobject. The socket is first checked to
		 ensure writability before sending. If the socket is not writable, NotWritableError is raised. Usage of this method requires a connected socket



- **recvfrom**(self, buffer_size=0):

		  Receives data from a host. For Udp sockets this method is event triggered
		 and called when the socket becomes readable according to select.select. Subclasses
		 should extend this method to customize functionality for when data is received.



- **on_select**(self):

		  Used to customize behavior when a socket is readable according to select.select.
		 It is not likely that one would overload this method; End users probably want
		 to overload recv/recvfrom instead.



- **delete**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Tcp_Client
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

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.network.Tcp_Client', class 'mpre.network.Tcp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Tcp_Socket
--------
	No docstring found

Default values for newly created instances:

- timeout                  : 0
- memory_mode              : -1
- deleted                  : False
- add_on_init              : True
- memory_size              : 0
- interface                : 0.0.0.0
- socket_family            : 2
- port                     : 0
- connection_attempts      : 10
- network_packet_size      : 32768
- added_to_network         : False
- verbosity                : 
- bind_on_init             : False
- socket_type              : 1
- _connecting              : False
- blocking                 : 0
- network_buffer           : 
- closed                   : False

This object defines the following non-private methods:


- **on_select**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.network.Tcp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Udp_Socket
--------
	No docstring found

Default values for newly created instances:

- timeout                  : 0
- memory_mode              : -1
- deleted                  : False
- add_on_init              : True
- memory_size              : 0
- interface                : 0.0.0.0
- port                     : 0
- network_packet_size      : 32768
- added_to_network         : False
- verbosity                : 
- bind_on_init             : True
- _connecting              : False
- blocking                 : 0
- network_buffer           : 
- closed                   : False

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')
