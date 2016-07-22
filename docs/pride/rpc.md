pride.rpc
==============

 pride.rpc - Remote Procedure Call portal built on top of pride.networkssl ssl sockets. 

DEFAULT_SERIALIZER
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.rpc.Serializer'>, <type 'object'>)

- **save_data**(args):

				No documentation available


- **load_data**(packed_data):

				No documentation available


Packet_Client
--------------

	 An SSL_Client that uses packetized send and recv (client side) 


Instance defaults: 

	{'_old_data': '',
	 'as_port': 0,
	 'auto_connect': True,
	 'blocking': 0,
	 'bypass_network_stack': True,
	 'ca_certs': None,
	 'cert_reqs': 0,
	 'certfile': None,
	 'check_hostname': False,
	 'ciphers': None,
	 'connect_timeout': 1,
	 'deleted': False,
	 'do_handshake_on_connect': False,
	 'dont_save': True,
	 'host_info': (),
	 'interface': '0.0.0.0',
	 'ip': '',
	 'keyfile': None,
	 'parse_args': False,
	 'port': 80,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'server_hostname': None,
	 'server_side': False,
	 'shutdown_flag': 2,
	 'shutdown_on_close': True,
	 'socket_family': 2,
	 'socket_type': 1,
	 'ssl_authenticated': False,
	 'ssl_version': 2,
	 'startup_components': (),
	 'suppress_ragged_eofs': True,
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.rpc.Packet_Client'>,
	 <class 'pride.networkssl.SSL_Client'>,
	 <class 'pride.network.Tcp_Client'>,
	 <class 'pride.network.Tcp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **_recv**(self, buffer_size):

				No documentation available


- **_send**(self, data):

				No documentation available


Packet_Socket
--------------

	 An SSL_Socket that uses packetized send and recv (server side) 


Instance defaults: 

	{'_old_data': '',
	 'blocking': 0,
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
	 'ssl_authenticated': False,
	 'startup_components': (),
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.rpc.Packet_Socket'>,
	 <class 'pride.networkssl.SSL_Socket'>,
	 <class 'pride.network.Tcp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **_recv**(self, buffer_size):

				No documentation available


- **_send**(self, data):

				No documentation available


Rpc_Client
--------------

	 Client socket for making rpc requests using packetized tcp stream. 


Instance defaults: 

	{'_old_data': '',
	 'as_port': 0,
	 'auto_connect': True,
	 'blocking': 0,
	 'bypass_network_stack': True,
	 'ca_certs': None,
	 'cert_reqs': 0,
	 'certfile': None,
	 'check_hostname': False,
	 'ciphers': None,
	 'connect_timeout': 1,
	 'deleted': False,
	 'do_handshake_on_connect': False,
	 'dont_save': True,
	 'host_info': (),
	 'interface': '0.0.0.0',
	 'ip': '',
	 'keyfile': None,
	 'parse_args': False,
	 'port': 80,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'server_hostname': None,
	 'server_side': False,
	 'shutdown_flag': 2,
	 'shutdown_on_close': True,
	 'socket_family': 2,
	 'socket_type': 1,
	 'ssl_authenticated': False,
	 'ssl_version': 2,
	 'startup_components': (),
	 'suppress_ragged_eofs': True,
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.rpc.Rpc_Client'>,
	 <class 'pride.rpc.Packet_Client'>,
	 <class 'pride.networkssl.SSL_Client'>,
	 <class 'pride.network.Tcp_Client'>,
	 <class 'pride.network.Tcp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **on_ssl_authentication**(self):

				No documentation available


- **recv**(self, packet_count):

				No documentation available


- **make_request**(self, request, callback_owner):

		 Send request to remote host and queue callback_owner for callback 


- **handle_exception**(self, _call, callback, response):

				No documentation available


- **deserealize**(self, response):

				No documentation available


Rpc_Connection_Manager
--------------

	 Creates Rpc_Clients for making rpc requests. Used to facilitate the
        the usage of a single connection for arbitrary requests to the host. 


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'requester_type': 'pride.rpc.Rpc_Client',
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.rpc.Rpc_Connection_Manager'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **get_host**(self, host_info):

				No documentation available


- **add**(self, _object):

				No documentation available


- **remove**(self, _object):

				No documentation available


Rpc_Server
--------------

	 Creates Rpc_Sockets for handling rpc requests. By default, this
        server runs on the localhost only, meaning it is not accessible 
        from the network. 


Instance defaults: 

	{'Tcp_Socket_type': 'pride.rpc.Rpc_Socket',
	 'allow_port_zero': False,
	 'backlog': 50,
	 'blocking': 0,
	 'bypass_network_stack': True,
	 'ca_certs': None,
	 'cert_reqs': 0,
	 'certfile': 'c:\\users\\_\\pythonbs\\pride\\ssl_server.crt',
	 'check_hostname': False,
	 'ciphers': None,
	 'connect_timeout': 1,
	 'deleted': False,
	 'do_handshake_on_connect': False,
	 'dont_save': False,
	 'interface': 'localhost',
	 'keyfile': 'c:\\users\\_\\pythonbs\\pride\\ssl_server.key',
	 'parse_args': False,
	 'port': 40022,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'reuse_port': 0,
	 'server_hostname': None,
	 'server_side': True,
	 'shutdown_flag': 2,
	 'shutdown_on_close': False,
	 'socket_family': 2,
	 'socket_type': 1,
	 'ssl_authenticated': False,
	 'ssl_version': 2,
	 'startup_components': (),
	 'suppress_ragged_eofs': True,
	 'timeout': 0,
	 'update_site_config_on_new_certfile': True,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.rpc.Rpc_Server'>,
	 <class 'pride.networkssl.SSL_Server'>,
	 <class 'pride.network.Server'>,
	 <class 'pride.network.Tcp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

Rpc_Socket
--------------

	 Packetized tcp socket for receiving and delegating rpc requests 


Instance defaults: 

	{'_old_data': '',
	 'blocking': 0,
	 'bypass_network_stack': True,
	 'connect_timeout': 1,
	 'deleted': False,
	 'dont_save': True,
	 'idle_after': 600,
	 'interface': '0.0.0.0',
	 'parse_args': False,
	 'port': 0,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'shutdown_flag': 2,
	 'shutdown_on_close': True,
	 'socket_family': 2,
	 'socket_type': 1,
	 'ssl_authenticated': False,
	 'startup_components': (),
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.rpc.Rpc_Socket'>,
	 <class 'pride.rpc.Packet_Socket'>,
	 <class 'pride.networkssl.SSL_Socket'>,
	 <class 'pride.network.Tcp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **check_idle**(self):

				No documentation available


- **serialize**(self, result):

				No documentation available


- **on_ssl_authentication**(self):

				No documentation available


- **recv**(self, packet_count):

				No documentation available


- **delete**(self):

				No documentation available


Rpc_Worker
--------------

	 Performs remote procedure call requests 


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.rpc.Rpc_Worker'>, <class 'pride.base.Base'>, <type 'object'>)

- **handle_request**(self, peername, session_id, component_name, method, serialized_arguments):

				No documentation available


- **deserealize**(self, serialized_arguments):

				No documentation available


Session
--------------

	 Maintains session id information and prepares outgoing requests 


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'host_info': None,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'requester_type': 'pride.rpc.Rpc_Client',
	 'session_id': None,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.rpc.Session'>, <class 'pride.base.Base'>, <type 'object'>)

- **next_callback**(self):

				No documentation available


- **execute**(self, instruction, callback):

		 Prepare instruction as a request to be sent by an Rpc_Client. A 
            request consists of session id information (size and id#), 
            followed by the information from the supplied instruction. No
            information regarding the callback is included in the request. 


UnauthorizedError
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.rpc.UnauthorizedError'>,
	 <type 'exceptions.Warning'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

packetize_recv
--------------

**packetize_recv**(recv):

		 Decorator that breaks a tcp stream into packets based on packet sizes,
        as supplied by the corresponding packetize_send decorator. In the event
        less then an entire packet is received, the received data is stored 
        until the remainder is received.
        
        The recv method decorated by this function will return a list of
        packets received or an empty list if no complete packets have been
        received. 


packetize_send
--------------

**packetize_send**(send):

		 Decorator that transforms a tcp stream into packets. Requires the use
        of the packetize_recv decorator on the recv end. 
