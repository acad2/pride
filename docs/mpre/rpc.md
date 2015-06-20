mpre.rpc
==============



RPC_Handler
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'replace_reference_on_load': True,
	 'servers': {'Tcp': 'mpre.rpc.RPC_Server'},
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.rpc.RPC_Handler'>, <class 'mpre.base.Base'>, <type 'object'>)

- **make_request**(self, callback, host_info, transport_protocol, component_name, method, args, kwargs):

				No documentation available


RPC_Request
--------------

	No docstring found


Instance defaults: 

	{'_connecting': False,
	 '_deleted': False,
	 'add_on_init': True,
	 'added_to_network': False,
	 'bind_on_init': False,
	 'blocking': 0,
	 'closed': False,
	 'connection_attempts': 10,
	 'delete_verbosity': 'vv',
	 'dont_save': True,
	 'interface': '0.0.0.0',
	 'port': 0,
	 'protocol': 0,
	 'recv_packet_size': 32768,
	 'recvfrom_packet_size': 65535,
	 'replace_reference_on_load': False,
	 'rpc_verbosity': 'v',
	 'socket_family': 2,
	 'socket_type': 1,
	 'timeout': 0,
	 'verbosity': '',
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.rpc.RPC_Request'>,
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

	{'_connecting': False,
	 '_deleted': False,
	 'add_on_init': True,
	 'added_to_network': False,
	 'as_port': 0,
	 'auto_connect': True,
	 'bind_on_init': False,
	 'blocking': 0,
	 'closed': False,
	 'connection_attempts': 10,
	 'delete_verbosity': 'vv',
	 'dont_save': True,
	 'interface': '0.0.0.0',
	 'ip': '',
	 'port': 80,
	 'protocol': 0,
	 'recv_packet_size': 32768,
	 'recvfrom_packet_size': 65535,
	 'replace_reference_on_load': False,
	 'socket_family': 2,
	 'socket_type': 1,
	 'target': (),
	 'timeout': 0,
	 'verbosity': '',
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.rpc.RPC_Requester'>,
	 <class 'mpre.network.Tcp_Client'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_connect**(self):

				No documentation available


- **recv**(self, buffer_size):

				No documentation available


RPC_Server
--------------

	No docstring found


Instance defaults: 

	{'Tcp_Socket_type': 'mpre.rpc.RPC_Request',
	 '_connecting': False,
	 '_deleted': False,
	 'add_on_init': True,
	 'added_to_network': False,
	 'backlog': 50,
	 'bind_on_init': False,
	 'blocking': 0,
	 'closed': False,
	 'connection_attempts': 10,
	 'delete_verbosity': 'vv',
	 'dont_save': True,
	 'interface': 'localhost',
	 'port': 40022,
	 'protocol': 0,
	 'recv_packet_size': 32768,
	 'recvfrom_packet_size': 65535,
	 'replace_reference_on_load': False,
	 'reuse_port': 0,
	 'socket_family': 2,
	 'socket_type': 1,
	 'timeout': 0,
	 'verbosity': '',
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.rpc.RPC_Server'>,
	 <class 'mpre.network.Server'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)