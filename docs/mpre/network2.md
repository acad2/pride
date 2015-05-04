mpre.network2
==============



- **Authenticated**(function):

		No documentation available


Authenticated_Client
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'email': '',
	 'password': '',
	 'replace_reference_on_load': True,
	 'target': 'Authenticated_Service',
	 'username': '',
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.network2.Authenticated_Client'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **login_result**(self, sender, packet):

		No documentation available


- **register**(self, sender, packet):

		No documentation available


- **register_results**(self, sender, packet):

		No documentation available


- **login**(self, sender, packet):

		No documentation available


Authenticated_Service
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'database_filename': ':memory:',
	 'hash_rounds': 100000,
	 'login_message': 'login success',
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.network2.Authenticated_Service'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_load**(self, attributes):

		No documentation available


- **register**(self, sender, packet):

		No documentation available


- **logout**(self, sender, packet):

		No documentation available


- **login**(self, sender, packet):

		No documentation available


- **call**(instance, sender, packet):

		No documentation available


Instruction
--------------

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


Method resolution order: 

	(<class 'mpre.Instruction'>, <type 'object'>)

- **execute**(self, priority, callback, host_info, transport_protocol):

		 usage: instruction.execute(priority=0.0, callback=None)
        
            Submits an instruction to the processing queue. The instruction
            will be executed in priority seconds. An optional callback function 
            can be provided if the return value of the instruction is needed.


Latency
--------------

	 usage: Latency([name="component_name"], 
                       [average_size=20]) => latency_object
                       
        Latency objects possess a latency attribute that marks
        the average time between calls to latency.update()


Method resolution order: 

	(<class 'mpre.utilities.Latency'>, <type 'object'>)

- **update**(self):

		 usage: latency.update()
        
            notes the current time and adds it to the average time.


- **display**(self, mode):

		 usage: latency.display([mode='sys.stdin'])
        
            Writes latency information via either sys.stdin.write or print.
            Information includes the latency average, meta average, and max value


Network_Service
--------------

	 Reliable udp socket; under development


Instance defaults: 

	{'_connecting': False,
	 '_deleted': False,
	 'add_on_init': True,
	 'added_to_network': False,
	 'bind_on_init': True,
	 'blocking': 0,
	 'closed': False,
	 'interface': '0.0.0.0',
	 'network_buffer': '',
	 'network_packet_size': 32768,
	 'port': 0,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'socket_family': 2,
	 'socket_type': 1,
	 'timeout': 0,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.network2.Network_Service'>,
	 <class 'mpre.network.Udp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **invalid_request**(self, sender, packet):

		No documentation available


- **socket_recv**(self):

		No documentation available


- **send_data**(self, data, to, response_to, expect_response):

		No documentation available


- **demo_reaction**(self, sender, packet):

		No documentation available


RPC_Handler
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False, 'replace_reference_on_load': True, 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.network2.RPC_Handler'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

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
	 'interface': '0.0.0.0',
	 'network_buffer': '',
	 'network_packet_size': 32768,
	 'port': 0,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'socket_family': 2,
	 'socket_type': 1,
	 'timeout': 0,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.network2.RPC_Request'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **recv**(self, network_packet_size):

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
	 'bad_target_verbosity': 0,
	 'bind_on_init': False,
	 'blocking': 0,
	 'closed': False,
	 'connection_attempts': 10,
	 'ip': '',
	 'network_buffer': '',
	 'network_packet_size': 32768,
	 'port': 80,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'socket_family': 2,
	 'socket_type': 1,
	 'target': (),
	 'timeout': 0,
	 'timeout_notify': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.network2.RPC_Requester'>,
	 <class 'mpre.network.Tcp_Client'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_connect**(self):

		No documentation available


- **recv**(self, network_packet_size):

		No documentation available


RPC_Server
--------------

	No docstring found


Instance defaults: 

	{'Tcp_Socket_type': 'network.Tcp_Socket',
	 '_connecting': False,
	 '_deleted': False,
	 'add_on_init': True,
	 'added_to_network': False,
	 'backlog': 50,
	 'bind_on_init': False,
	 'blocking': 0,
	 'closed': False,
	 'connection_attempts': 10,
	 'interface': '0.0.0.0',
	 'name': '',
	 'network_buffer': '',
	 'network_packet_size': 32768,
	 'port': 80,
	 'protocol': 0,
	 'replace_reference_on_load': True,
	 'reuse_port': 0,
	 'share_methods': ('on_connect', 'client_socket_recv', 'client_socket_send'),
	 'socket_family': 2,
	 'socket_type': 1,
	 'timeout': 0,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.network2.RPC_Server'>,
	 <class 'mpre.network.Server'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)