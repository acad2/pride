mpre.rpc
==============



Environment_Access
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'allow_registration': True,
	 'database_name': '',
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'login_message': '',
	 'protocol_component': 'Secure_Remote_Password',
	 'replace_reference_on_load': True,
	 'requester_address': None}

Method resolution order: 

	(<class 'mpre.rpc.Environment_Access'>,
	 <class 'mpre.authentication.Authenticated_Service'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **call**(instance, *args, **kwargs):

				No documentation available


- **call**(instance, *args, **kwargs):

				No documentation available


Environment_Access_Client
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'auto_login': True,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'ip': 'localhost',
	 'logged_in': False,
	 'password': '',
	 'password_prompt': '{}: Please provide the pass phrase or word: ',
	 'port': 40022,
	 'protocol_client': 'mpre.srp.SRP_Client',
	 'replace_reference_on_load': True,
	 'target_service': 'Environment_Access',
	 'username': ''}

Method resolution order: 

	(<class 'mpre.rpc.Environment_Access_Client'>,
	 <class 'mpre.authentication.Authenticated_Client'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

RPC_Handler
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'current_connections': None,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'environment_access_client_type': 'mpre.rpc.Environment_Access_Client',
	 'remote_hosts': (),
	 'replace_reference_on_load': True,
	 'require_environment_access': True,
	 'servers': {'tcp': 'mpre.rpc.RPC_Server'}}

Method resolution order: 

	(<class 'mpre.rpc.RPC_Handler'>, <class 'mpre.base.Base'>, <type 'object'>)

- **make_request**(self, callback, host_info, transport_protocol, priority_flag, component_name, method, args, kwargs):

				No documentation available


- **delete**(self):

				No documentation available


RPC_Request
--------------

	No docstring found


Instance defaults: 

	{'_byte_count': 0,
	 '_connecting': False,
	 '_deleted': False,
	 'add_on_init': True,
	 'added_to_network': False,
	 'bind_on_init': False,
	 'blocking': 0,
	 'closed': False,
	 'connected': False,
	 'connection_attempts': 10,
	 'delete_verbosity': 'vv',
	 'dont_save': True,
	 'interface': '0.0.0.0',
	 'port': 0,
	 'protocol': 0,
	 'replace_reference_on_load': False,
	 'rpc_verbosity': 'vv',
	 'socket_family': 2,
	 'socket_type': 1,
	 'ssl_authenticated': False,
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.rpc.RPC_Request'>,
	 <class 'mpre.networkssl.SSL_Socket'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **recv**(self, buffer_size):

				No documentation available


RPC_Requester
--------------

	No docstring found


Instance defaults: 

	{'_byte_count': 0,
	 '_connecting': False,
	 '_deleted': False,
	 'add_on_init': True,
	 'added_to_network': False,
	 'as_port': 0,
	 'authentication_client': 'mpre.rpc.Environment_Access_Client',
	 'auto_connect': True,
	 'bind_on_init': False,
	 'blocking': 0,
	 'ca_certs': None,
	 'callback': None,
	 'cert_reqs': 0,
	 'certfile': None,
	 'check_hostname': False,
	 'ciphers': None,
	 'closed': False,
	 'connected': False,
	 'connection_attempts': 10,
	 'delete_verbosity': 'vv',
	 'do_handshake_on_connect': False,
	 'dont_save': True,
	 'interface': '0.0.0.0',
	 'ip': '',
	 'keyfile': None,
	 'port': 80,
	 'protocol': 0,
	 'replace_reference_on_load': False,
	 'server_hostname': None,
	 'server_side': False,
	 'socket_family': 2,
	 'socket_type': 1,
	 'ssl_authenticated': False,
	 'ssl_version': 2,
	 'suppress_ragged_eofs': True,
	 'target': (),
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.rpc.RPC_Requester'>,
	 <class 'mpre.networkssl.SSL_Client'>,
	 <class 'mpre.network.Tcp_Client'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_authentication**(self):

				No documentation available


- **recv**(self, buffer_size):

				No documentation available


- **make_request**(self, callback, request, high_priority):

				No documentation available


RPC_Server
--------------

	No docstring found


Instance defaults: 

	{'Tcp_Socket_type': 'mpre.rpc.RPC_Request',
	 '_byte_count': 0,
	 '_connecting': False,
	 '_deleted': False,
	 'add_on_init': True,
	 'added_to_network': False,
	 'allow_port_zero': False,
	 'backlog': 50,
	 'bind_on_init': False,
	 'blocking': 0,
	 'ca_certs': None,
	 'cert_reqs': 0,
	 'certfile': 'server.crt',
	 'check_hostname': False,
	 'ciphers': None,
	 'closed': False,
	 'connected': False,
	 'connection_attempts': 10,
	 'delete_verbosity': 'vv',
	 'do_handshake_on_connect': False,
	 'dont_save': False,
	 'interface': 'localhost',
	 'keyfile': 'server.key',
	 'port': 40022,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'reuse_port': 0,
	 'server_hostname': None,
	 'server_side': True,
	 'socket_family': 2,
	 'socket_type': 1,
	 'ssl_authenticated': False,
	 'ssl_version': 2,
	 'suppress_ragged_eofs': True,
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.rpc.RPC_Server'>,
	 <class 'mpre.networkssl.SSL_Server'>,
	 <class 'mpre.network.Server'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)