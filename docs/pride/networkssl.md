pride.networkssl
==============



SSL_Client
--------------

	 An asynchronous client side Tcp socket wrapped in an ssl socket.
        Users should extend on_ssl_authentication instead of on_connect to
        initiate data transfer; on_connect is used to start the
        ssl handshake


Instance defaults: 

	{'as_port': 0,
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

	(<class 'pride.networkssl.SSL_Client'>,
	 <class 'pride.network.Tcp_Client'>,
	 <class 'pride.network.Tcp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **on_select**(self):

				No documentation available


- **on_ssl_authentication**(self):

				No documentation available


- **on_connect**(self):

				No documentation available


- **ssl_connect**(self):

				No documentation available


SSL_Server
--------------

	No docstring found


Instance defaults: 

	{'Tcp_Socket_type': 'pride.networkssl.SSL_Socket',
	 'allow_port_zero': False,
	 'backlog': 50,
	 'blocking': 0,
	 'bypass_network_stack': True,
	 'ca_certs': None,
	 'cert_reqs': 0,
	 'certfile': '',
	 'check_hostname': False,
	 'ciphers': None,
	 'connect_timeout': 1,
	 'deleted': False,
	 'do_handshake_on_connect': False,
	 'dont_save': False,
	 'interface': '0.0.0.0',
	 'keyfile': '',
	 'parse_args': False,
	 'port': 443,
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

	(<class 'pride.networkssl.SSL_Server'>,
	 <class 'pride.network.Server'>,
	 <class 'pride.network.Tcp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **on_load**(self, state):

				No documentation available


SSL_Socket
--------------

	 An asynchronous server side client socket wrapped in an ssl socket.
        Users should override the on_ssl_authentication method instead of
        on_connect. 


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
	 'ssl_authenticated': False,
	 'startup_components': (),
	 'timeout': 0,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.networkssl.SSL_Socket'>,
	 <class 'pride.network.Tcp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **on_select**(self):

				No documentation available


- **on_ssl_authentication**(self):

				No documentation available


- **on_connect**(self):

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
