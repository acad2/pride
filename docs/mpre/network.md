mpre.network
==============



Average
--------------

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


Method resolution order: 

	(<class 'mpre.utilities.Average'>, <type 'object'>)

- **full_add**(self, value):

				No documentation available


- **partial_add**(self, value):

				No documentation available


Error_Handler
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.network.Error_Handler'>, <type 'object'>)

- **connection_reset**(self, sock, error):

				No documentation available


- **unhandled**(self, sock, error):

				No documentation available


- **bad_target**(self, sock, error):

				No documentation available


- **connection_closed**(self, sock, error):

				No documentation available


- **connection_was_aborted**(self, sock, error):

				No documentation available


- **eagain**(self, sock, error):

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
            
            host_info may be specified to designate a remote machine that
            the Instruction should be executed on. If host_info is supplied
            and callback is None, the results of the instruction will be 
            supplied to RPC_Handler.alert.


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


Multicast_Beacon
--------------

	No docstring found


Instance defaults: 

	{'_connecting': False,
	 '_deleted': False,
	 'add_on_init': True,
	 'added_to_network': False,
	 'bind_on_init': True,
	 'blocking': 0,
	 'closed': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'interface': '0.0.0.0',
	 'multicast_group': '224.0.0.0',
	 'multicast_port': 1929,
	 'packet_ttl': '\x7f',
	 'port': 0,
	 'protocol': 0,
	 'recv_packet_size': 32768,
	 'recvfrom_packet_size': 65535,
	 'replace_reference_on_load': False,
	 'socket_family': 2,
	 'socket_type': 1,
	 'timeout': 0,
	 'verbosity': '',
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.network.Multicast_Beacon'>,
	 <class 'mpre.network.Udp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Multicast_Receiver
--------------

	No docstring found


Instance defaults: 

	{'_connecting': False,
	 '_deleted': False,
	 'add_on_init': True,
	 'added_to_network': False,
	 'address': '224.0.0.0',
	 'bind_on_init': True,
	 'blocking': 0,
	 'closed': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'interface': '0.0.0.0',
	 'port': 0,
	 'protocol': 0,
	 'recv_packet_size': 32768,
	 'recvfrom_packet_size': 65535,
	 'replace_reference_on_load': False,
	 'socket_family': 2,
	 'socket_type': 1,
	 'timeout': 0,
	 'verbosity': '',
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.network.Multicast_Receiver'>,
	 <class 'mpre.network.Udp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Network
--------------

	 Manages socket objects and is responsible for calling select.select to determine
        readability/writability of sockets. Also responsible for non blocking connect logic. 
        This component is created by default upon application startup, and in most cases will
        not require user interaction.


Instance defaults: 

	{'_deleted': False,
	 '_updating': False,
	 'auto_start': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'number_of_sockets': 0,
	 'priority': 0.01,
	 'replace_reference_on_load': True,
	 'run_callback': None,
	 'running': True,
	 'update_priority': 5,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.network.Network'>,
	 <class 'mpre.vmlibrary.Process'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **run**(self):

				No documentation available


- **remove**(self, sock):

				No documentation available


- **add**(self, sock):

				No documentation available


- **delete**(self):

				No documentation available


NotWritableError
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.network.NotWritableError'>,
	 <type 'exceptions.IOError'>,
	 <type 'exceptions.EnvironmentError'>,
	 <type 'exceptions.StandardError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

Packet_Sniffer
--------------

	No docstring found


Instance defaults: 

	{'IP_HDRINCL': 1,
	 '_connecting': False,
	 '_deleted': False,
	 'add_on_init': True,
	 'added_to_network': False,
	 'bind_on_init': False,
	 'blocking': 0,
	 'closed': False,
	 'connection_attempts': 10,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'interface': '0.0.0.0',
	 'port': 0,
	 'protocol': 0,
	 'recv_packet_size': 32768,
	 'recvfrom_packet_size': 65535,
	 'replace_reference_on_load': False,
	 'socket_family': 2,
	 'socket_type': 3,
	 'timeout': 0,
	 'verbosity': '',
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.network.Packet_Sniffer'>,
	 <class 'mpre.network.Raw_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **close**(self):

				No documentation available


Raw_Socket
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
	 'dont_save': False,
	 'interface': '0.0.0.0',
	 'port': 0,
	 'protocol': 0,
	 'recv_packet_size': 32768,
	 'recvfrom_packet_size': 65535,
	 'replace_reference_on_load': False,
	 'socket_family': 2,
	 'socket_type': 3,
	 'timeout': 0,
	 'verbosity': '',
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.network.Raw_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Server
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
	 'delete_verbosity': 'vv',
	 'dont_save': True,
	 'interface': '0.0.0.0',
	 'port': 80,
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

	(<class 'mpre.network.Server'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_connect**(self, connection, address):

		 Connection logic that the server should apply when a new client has connected.
            This method should be overloaded by subclasses


- **accept**(self):

				No documentation available


- **handle_bind_error**(self):

				No documentation available


- **on_select**(self):

				No documentation available


Socket
--------------

	 Provides a mostly transparent asynchronous socket interface by applying a 
        Wrapper to a _socketobject. The default socket family is socket.AF_INET and
        the default socket type is socket.SOCK_STREAM (a tcp socket).


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
	 'dont_save': False,
	 'interface': '0.0.0.0',
	 'port': 0,
	 'protocol': 0,
	 'recv_packet_size': 32768,
	 'recvfrom_packet_size': 65535,
	 'replace_reference_on_load': False,
	 'socket_family': 2,
	 'socket_type': 1,
	 'timeout': 0,
	 'verbosity': '',
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_connect**(self):

		 Performs any logic required when a Tcp connection succeeds. This method should
            be overloaded by subclasses.


- **connect**(self, address):

		 Perform a non blocking connect to the specified address. The on_connect method
            is called when the connection succeeds, or the appropriate error handler method
            is called if the connection fails. Subclasses should overload on_connect instead
            of this method.


- **close**(self):

				No documentation available


- **recv**(self, buffer_size):

		 Receives data from a remote endpoint. This method is event triggered and called
            when the socket becomes readable according to select.select. This
            method is called for Tcp sockets and requires a connection.
            
            Note that this recv will return the entire contents of the OS buffer and 
            does not need to be called in a loop.


- **recvfrom**(self, buffer_size):

		 Receives data from a host. For Udp sockets this method is event triggered
            and called when the socket becomes readable according to select.select. Subclasses
            should extend this method to customize functionality for when data is received.


- **on_select**(self):

		 Used to customize behavior when a socket is readable according to select.select.
            It is not likely that one would overload this method; End users probably want
            to overload recv/recvfrom instead.


- **delete**(self):

				No documentation available


Tcp_Client
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

	(<class 'mpre.network.Tcp_Client'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Tcp_Socket
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
	 'socket_family': 2,
	 'socket_type': 1,
	 'timeout': 0,
	 'verbosity': '',
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_select**(self):

				No documentation available


Udp_Socket
--------------

	No docstring found


Instance defaults: 

	{'_connecting': False,
	 '_deleted': False,
	 'add_on_init': True,
	 'added_to_network': False,
	 'bind_on_init': True,
	 'blocking': 0,
	 'closed': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'interface': '0.0.0.0',
	 'port': 0,
	 'protocol': 0,
	 'recv_packet_size': 32768,
	 'recvfrom_packet_size': 65535,
	 'replace_reference_on_load': False,
	 'socket_family': 2,
	 'socket_type': 1,
	 'timeout': 0,
	 'verbosity': '',
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.network.Udp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)