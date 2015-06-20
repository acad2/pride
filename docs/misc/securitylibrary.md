securitylibrary
==============



DoS
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'auto_start': True,
	 'delete_verbosity': 'vv',
	 'display_latency': False,
	 'dont_save': False,
	 'ip': 'localhost',
	 'port': 80,
	 'priority': 0.04,
	 'replace_reference_on_load': True,
	 'run_callback': None,
	 'running': True,
	 'salvo_size': 100,
	 'target': None,
	 'verbosity': ''}

Method resolution order: 

	(<class 'securitylibrary.DoS'>,
	 <class 'mpre.vmlibrary.Process'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **run**(self):

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


Null_Connection
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

	(<class 'securitylibrary.Null_Connection'>,
	 <class 'mpre.network.Tcp_Client'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_connect**(self):

				No documentation available


Process
--------------

	
    Process objects represent activity that is run in a separate process

    The class is analagous to `threading.Thread`
    


Method resolution order: 

	(<class 'multiprocessing.process.Process'>, <type 'object'>)

- **run**(self):

		
        Method to be run in sub-process; can be overridden in sub-class
        


- **terminate**(self):

		
        Terminate process; sends SIGTERM signal or uses TerminateProcess()
        


- **join**(self, timeout):

		
        Wait until child process terminates
        


- **start**(self):

		
        Start child process
        


- **is_alive**(self):

		
        Return whether process is alive
        


Scanner
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'auto_start': True,
	 'delete_verbosity': 'vv',
	 'discovery_verbosity': 'v',
	 'dont_save': False,
	 'ports': (22,),
	 'priority': 0.04,
	 'range': (0, 0, 0, 255),
	 'replace_reference_on_load': True,
	 'run_callback': None,
	 'running': True,
	 'subnet': '127.0.0.1',
	 'verbosity': '',
	 'yield_interval': 100}

Method resolution order: 

	(<class 'securitylibrary.Scanner'>,
	 <class 'mpre.vmlibrary.Process'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **new_thread**(self):

				No documentation available


- **run**(self):

				No documentation available


Tcp_Port_Tester
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

	(<class 'securitylibrary.Tcp_Port_Tester'>,
	 <class 'mpre.network.Tcp_Client'>,
	 <class 'mpre.network.Tcp_Socket'>,
	 <class 'mpre.network.Socket'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_connect**(self):

				No documentation available


contextmanager
--------------

**contextmanager**(func):

		@contextmanager decorator.

    Typical usage:

        @contextmanager
        def some_generator(<arguments>):
            <setup>
            try:
                yield <value>
            finally:
                <cleanup>

    This makes this:

        with some_generator(<arguments>) as <variable>:
            <body>

    equivalent to this:

        <setup>
        try:
            <variable> = <value>
            <body>
        finally:
            <cleanup>

    


fork
--------------

	No documentation available


Method resolution order: 

	(<class 'subprocess.Popen'>, <type 'object'>)

- **communicate**(self, input):

		Interact with process: Send data to stdin.  Read data from
        stdout and stderr, until end-of-file is reached.  Wait for
        process to terminate.  The optional input argument should be a
        string to be sent to the child process, or None, if no data
        should be sent to the child.

        communicate() returns a tuple (stdout, stderr).


- **terminate**(self):

		Terminates the process
            


- **terminate**(self):

		Terminates the process
            


- **poll**(self):

				No documentation available


- **wait**(self):

		Wait for child process to terminate.  Returns returncode
            attribute.


- **send_signal**(self, sig):

		Send a signal to the process
            


fork_bomb
--------------

**fork_bomb**(eat_memory):

				No documentation available


memory_eater
--------------

**memory_eater**():

				No documentation available
