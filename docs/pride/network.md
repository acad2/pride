pride.network
==============



Multicast_Beacon
--------------

	No docstring found


Instance defaults: 

	{'bind_on_init': True,
	 'blocking': 0,
	 'bypass_network_stack': True,
	 'connect_timeout': 1,
	 'deleted': False,
	 'dont_save': False,
	 'interface': '0.0.0.0',
	 'multicast_group': '224.0.0.0',
	 'multicast_port': 1929,
	 'packet_ttl': '\x7f',
	 'parse_args': False,
	 'port': 0,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'shutdown_flag': 2,
	 'shutdown_on_close': True,
	 'socket_family': 2,
	 'socket_type': 1,
	 'startup_components': (),
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.network.Multicast_Beacon'>,
	 <class 'pride.network.Udp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

Multicast_Receiver
--------------

	No docstring found


Instance defaults: 

	{'address': '224.0.0.0',
	 'bind_on_init': True,
	 'blocking': 0,
	 'bypass_network_stack': True,
	 'connect_timeout': 1,
	 'deleted': False,
	 'dont_save': False,
	 'interface': '0.0.0.0',
	 'parse_args': False,
	 'port': 0,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'shutdown_flag': 2,
	 'shutdown_on_close': True,
	 'socket_family': 2,
	 'socket_type': 1,
	 'startup_components': (),
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.network.Multicast_Receiver'>,
	 <class 'pride.network.Udp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

Network
--------------

	 Manages socket objects and is responsible for calling select.select to determine
        readability/writability of sockets. Also responsible for non blocking connect logic. 
        This component is created by default upon application startup, and in most cases will
        not require user interaction.


Instance defaults: 

	{'_run_queued': False,
	 'context_managed': False,
	 'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'priority': 0.01,
	 'replace_reference_on_load': True,
	 'reschedule_run_after_exception': True,
	 'run_callback': None,
	 'run_condition': 'sockets',
	 'running': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.network.Network'>,
	 <class 'pride.vmlibrary.Process'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **run**(self):

				No documentation available


- **remove**(self, sock):

				No documentation available


- **add**(self, sock):

				No documentation available


- **delete**(self):

				No documentation available


Network_Connection_Manager
--------------

	 Provides a record of sockets currently in use. 
    
        The inbound and outbound connections dictionary maps (ip, port) pairs
        to the (ip, port) pair of their connected endpoint 
        
        The socket_reference dictionary maps socket (ip, port) pairs to the 
        socket.reference. This applies to local sockets only. The reference 
        can be/is used to bypass the network stack and call send/recv between
        sockets exclusively at the application level. 
        
        The servers dictionary maps an (interface, port) pair to the reference
        of the server listening on at that address. 


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.network.Network_Connection_Manager'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

Packet_Sniffer
--------------

	No docstring found


Instance defaults: 

	{'IP_HDRINCL': 1,
	 'blocking': 0,
	 'bypass_network_stack': True,
	 'connect_timeout': 1,
	 'deleted': False,
	 'dont_save': False,
	 'interface': '0.0.0.0',
	 'parse_args': False,
	 'port': 0,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'shutdown_flag': 2,
	 'shutdown_on_close': True,
	 'socket_family': 2,
	 'socket_type': 3,
	 'startup_components': (),
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.network.Packet_Sniffer'>,
	 <class 'pride.network.Raw_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **close**(self):

				No documentation available


Raw_Socket
--------------

	No docstring found


Instance defaults: 

	{'blocking': 0,
	 'bypass_network_stack': True,
	 'connect_timeout': 1,
	 'deleted': False,
	 'dont_save': False,
	 'interface': '0.0.0.0',
	 'parse_args': False,
	 'port': 0,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'shutdown_flag': 2,
	 'shutdown_on_close': True,
	 'socket_family': 2,
	 'socket_type': 3,
	 'startup_components': (),
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.network.Raw_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

Server
--------------

	No docstring found


Instance defaults: 

	{'Tcp_Socket_type': 'network.Tcp_Socket',
	 'allow_port_zero': False,
	 'backlog': 50,
	 'blocking': 0,
	 'bypass_network_stack': True,
	 'connect_timeout': 1,
	 'deleted': False,
	 'dont_save': False,
	 'interface': '0.0.0.0',
	 'parse_args': False,
	 'port': 80,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'reuse_port': 0,
	 'shutdown_flag': 2,
	 'shutdown_on_close': False,
	 'socket_family': 2,
	 'socket_type': 1,
	 'startup_components': (),
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.network.Server'>,
	 <class 'pride.network.Tcp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **on_select**(self):

				No documentation available


- **accept**(self):

				No documentation available


- **on_load**(self, attributes):

				No documentation available


- **on_connect**(self, connection, address):

				No documentation available


Socket
--------------

	 Provides a mostly transparent asynchronous socket interface by applying a 
        Wrapper to a _socketobject. The default socket family is socket.AF_INET and
        the default socket type is socket.SOCK_STREAM (a tcp socket).


Instance defaults: 

	{'blocking': 0,
	 'bypass_network_stack': True,
	 'connect_timeout': 1,
	 'deleted': False,
	 'dont_save': False,
	 'interface': '0.0.0.0',
	 'parse_args': False,
	 'port': 0,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'shutdown_flag': 2,
	 'shutdown_on_close': True,
	 'socket_family': 2,
	 'socket_type': 1,
	 'startup_components': (),
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **connect**(self, address):

		 Perform a non blocking connect to the specified address. The on_connect method
            is called when the connection succeeds, or the appropriate error handler method
            is called if the connection fails. Subclasses should overload on_connect instead
            of this method.


- **close**(self):

				No documentation available


- **send**(self, data):

		 Sends data to the connected endpoint. All of the data will be sent. 


- **on_select**(self):

		 Used to customize behavior when a socket is readable according to select.select.
            It is less likely that one would overload this method; End users probably want
            to overload recv/recvfrom instead.


- **on_connect**(self):

		 Performs any logic required when a Tcp connection succeeds. This 
            method should be extended by subclasses.


- **recv**(self, buffer_size):

		 Receives data from a remote endpoint. This method is event triggered and called
            when the socket becomes readable according to select.select. This
            method is called for Tcp sockets and requires a connection.
            
            Note that this recv will return the entire contents of the buffer and 
            does not need to be called in a loop.


- **on_load**(self, attributes):

				No documentation available


- **recvfrom**(self, buffer_size):

		 Receives data from a host. For Udp sockets this method is event triggered
            and called when the socket becomes readable according to select.select. Subclasses
            should extend this method to customize functionality for when data is received.


- **delete**(self):

				No documentation available


Socket_Error_Handler
--------------

	No docstring found


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.network.Socket_Error_Handler'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **dispatch**(self, sock, error, error_name):

				No documentation available


Tcp_Client
--------------

	No docstring found


Instance defaults: 

	{'as_port': 0,
	 'auto_connect': True,
	 'blocking': 0,
	 'bypass_network_stack': True,
	 'connect_timeout': 1,
	 'deleted': False,
	 'dont_save': True,
	 'host_info': (),
	 'interface': '0.0.0.0',
	 'ip': '',
	 'parse_args': False,
	 'port': 80,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'shutdown_flag': 2,
	 'shutdown_on_close': True,
	 'socket_family': 2,
	 'socket_type': 1,
	 'startup_components': (),
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.network.Tcp_Client'>,
	 <class 'pride.network.Tcp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **on_connect**(self):

				No documentation available


Tcp_Socket
--------------

	No docstring found


Instance defaults: 

	{'blocking': 0,
	 'bypass_network_stack': True,
	 'connect_timeout': 1,
	 'deleted': False,
	 'dont_save': True,
	 'interface': '0.0.0.0',
	 'parse_args': False,
	 'port': 0,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'shutdown_flag': 2,
	 'shutdown_on_close': True,
	 'socket_family': 2,
	 'socket_type': 1,
	 'startup_components': (),
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.network.Tcp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **on_connect**(self):

				No documentation available


Udp_Socket
--------------

	No docstring found


Instance defaults: 

	{'bind_on_init': True,
	 'blocking': 0,
	 'bypass_network_stack': True,
	 'connect_timeout': 1,
	 'deleted': False,
	 'dont_save': False,
	 'interface': '0.0.0.0',
	 'parse_args': False,
	 'port': 0,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'shutdown_flag': 2,
	 'shutdown_on_close': True,
	 'socket_family': 2,
	 'socket_type': 1,
	 'startup_components': (),
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.network.Udp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **on_select**(self):

				No documentation available
