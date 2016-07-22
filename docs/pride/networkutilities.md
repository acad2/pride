pride.networkutilities
==============



RTT_Test
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

	(<class 'pride.networkutilities.RTT_Test'>,
	 <class 'pride.network.Tcp_Client'>,
	 <class 'pride.network.Tcp_Socket'>,
	 <class 'pride.network.Socket'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **on_connect**(self):

				No documentation available


- **connect**(self, address):

				No documentation available


disable_metrics_cache
--------------

**disable_metrics_cache**(state):

				No documentation available


reload_with_changes
--------------

**reload_with_changes**():

				No documentation available


set_buffer_sizes
--------------

**set_buffer_sizes**(minimum_size, initial_size, maximum_size):

				No documentation available


set_connection_backlog
--------------

**set_connection_backlog**(backlog):

				No documentation available


set_file_handle_limit
--------------

**set_file_handle_limit**(limit):

				No documentation available


set_max_connection
--------------

**set_max_connection**(limit):

				No documentation available


set_packet_backlog
--------------

**set_packet_backlog**(backlog):

				No documentation available


set_timestamp_use
--------------

**set_timestamp_use**(flag):

				No documentation available


set_window_scaling
--------------

**set_window_scaling**(flag):

		Possible side effects per wikipedia:

       Because some routers and firewalls do not properly implement TCP Window Scaling, it can cause a user's Internet connection to malfunction intermittently for a few minutes, then appear to start working again for no reason. There is also an issue if a firewall doesn't support the TCP extensions.


shell
--------------

**shell**(command, shell):

		 usage: shell('command string --with args', 
                     [shell=False]) = > sys.stdout.output from executed command
                    
        Launches a process on the physical machine via the operating 
        system shell. The shell and available commands are OS dependent.
        
        Regarding the shell argument; from the python docs on subprocess.Popen:
            "The shell argument (which defaults to False) specifies whether to use the shell as the program to execute. If shell is True, it is recommended to pass args as a string rather than as a sequence."
            
        and also:        
            "Executing shell commands that incorporate unsanitized input from an untrusted source makes a program vulnerable to shell injection, a serious security flaw which can result in arbitrary command execution. For this reason, the use of shell=True is strongly discouraged in cases where the command string is constructed from external input" 


tune_tcp_performance
--------------

**tune_tcp_performance**(minimum_size, initial_size, maximum_size, window_scaling, use_timestamps, use_selective_ack, packet_backlog, metrics_cache_disabled):

				No documentation available


use_selective_acknowledgement
--------------

**use_selective_acknowledgement**(flag):

				No documentation available
