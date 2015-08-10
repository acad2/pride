mpre.networkssl
==============



SSL_Client
--------------

	 An asynchronous client side Tcp socket wrapped in an ssl socket.
        Users should extend on_authentication instead of on_connect to
        initiate data transfer; on_connect is used to start the
        ssl handshake


Instance defaults: 

	{'_byte_count': 0,
	 '_connecting': False,
	 '_deleted': False,
	 'add_on_init': True,
	 'added_to_network': False,
	 'as_port': 0,
	 'auto_connect': True,
	 'bind_on_init': False,
	 'blocking': 0,
	 'ca_certs': None,
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

	(<class 'mpre.networkssl.SSL_Client'>,
	 <class 'mpre.network.Tcp_Client'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_authentication**(self):

				No documentation available


- **on_connect**(self):

				No documentation available


- **on_select**(self):

				No documentation available


- **ssl_connect**(self):

				No documentation available


SSL_Server
--------------

	No docstring found


Instance defaults: 

	{'Tcp_Socket_type': 'mpre.networkssl.SSL_Socket',
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
	 'interface': '0.0.0.0',
	 'keyfile': 'server.key',
	 'port': 443,
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

	(<class 'mpre.networkssl.SSL_Server'>,
	 <class 'mpre.network.Server'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **accept**(self):

				No documentation available


SSL_Socket
--------------

	 An asynchronous server side client socket wrapped in an ssl socket.
        Users should override the on_authentication method instead of
        on_connect


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
	 'socket_family': 2,
	 'socket_type': 1,
	 'ssl_authenticated': False,
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.networkssl.SSL_Socket'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_authentication**(self):

				No documentation available


- **on_connect**(self):

				No documentation available


- **on_select**(self):

				No documentation available


- **ssl_connect**(self):

				No documentation available


generate_rsa_keypair
--------------

**generate_rsa_keypair**(name):

				No documentation available


generate_self_signed_certificate
--------------

**generate_self_signed_certificate**(name):

		 Creates a name.key, name.csr, and name.crt file. These files can
        be used for the keyfile and certfile options for an ssl server socket
