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
	 'target': None}

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
                           *args, **kwargs).execute(priority=priority,
                                                    callback=callback,
                                                    host_info=(ip, port))
                           
        Creates and executes an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        host_info may supply an ip address string and port number integer
        to execute the instruction on a remote machine. This requirements
        for this to be a success are:
            
            - The machine must have an instance of metapython running
            - The machine must be accessible via the network
            - The local machine must be registered and logged in to
              the remote machine
            - The local machine may need to be registered and logged in to
              have permission to the use the specific component and method
              in question
            - The local machine ip must not be blacklisted by the remote
              machine.
            - The remote machine may require that the local machine ip
              be in a whitelist to access the method in question.
              
        Other then the security requirements, remote procedure calls require 
        zero config on the part of either host. An object will be accessible
        if it exists on the machine in question.
              
        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed if the instruction is being executed
        locally. If the instruction is being executed remotely, this instead
        acts as a flag. If set to a True value, the instruction will be
        placed at the front of the local queue to be sent to the host.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds or sent to the machine in question. 
        
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

		 usage: instruction.execute(priority=0.0, callback=None,
                                       host_info=tuple())
        
            Submits an instruction to the processing queue. If being executed
            locally, the instruction will be executed in priority seconds. 
            An optional callback function can be provided if the return value 
            of the instruction is needed.
            
            host_info may be specified to designate a remote machine that
            the Instruction should be executed on. If being executed remotely, 
            priority is a high_priority flag where 0 means the instruction will
            be placed at the end of the rpc queue for the remote host in 
            question. If set, the instruction will instead be placed at the 
            beginning of the queue.
            
            Remotely executed instructions have a default callback, which is 
            the appropriate RPC_Requester.alert.
            
            The transport protocol flag is currently unused. Support for
            UDP and other protocols could be implemented and dispatched
            via this flag.


Latency
--------------

	 usage: Latency([name="component_name"], 
                       [size=20]) => latency_object
                       
        Latency objects possess a latency attribute that marks
        the average time between calls to latency.update()


Method resolution order: 

	(<class 'mpre.utilities.Latency'>, <type 'object'>)

- **finish_measuring**(self):

				No documentation available


- **start_measuring**(self):

				No documentation available


Null_Connection
--------------

	No docstring found


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
	 'closed': False,
	 'connected': False,
	 'connection_attempts': 10,
	 'delete_verbosity': 'vv',
	 'dont_save': True,
	 'interface': '0.0.0.0',
	 'ip': '',
	 'port': 80,
	 'protocol': 0,
	 'replace_reference_on_load': False,
	 'socket_family': 2,
	 'socket_type': 1,
	 'target': (),
	 'timeout': 0,
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

	{'_byte_count': 0,
	 '_connecting': False,
	 '_deleted': False,
	 'add_on_init': True,
	 'added_to_network': False,
	 'as_port': 0,
	 'auto_connect': True,
	 'bind_on_init': False,
	 'blocking': 0,
	 'closed': False,
	 'connected': False,
	 'connection_attempts': 10,
	 'delete_verbosity': 'vv',
	 'dont_save': True,
	 'interface': '0.0.0.0',
	 'ip': '',
	 'port': 80,
	 'protocol': 0,
	 'replace_reference_on_load': False,
	 'socket_family': 2,
	 'socket_type': 1,
	 'target': (),
	 'timeout': 0,
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
