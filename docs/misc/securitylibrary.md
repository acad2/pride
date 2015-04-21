mpre.misc.securitylibrary
========
No documentation available

DoS
--------
	No docstring found

Default values for newly created instances:

- count                    : 0
- timeout_notify           : False
- display_progress         : False
- salvo_size               : 100
- memory_mode              : -1
- deleted                  : False
- ip                       : localhost
- verbosity                : 
- priority                 : 0.04
- memory_size              : 4096
- auto_start               : True
- display_latency          : False
- port                     : 80
- target                   : None

This object defines the following non-private methods:


- **run**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.misc.securitylibrary.DoS', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Instruction
--------
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

Latency
--------
 usage: Latency([name="component_name"], 
                       [average_size=20]) => latency_object
                       
        Latency objects possess a latency attribute that marks
        the average time between calls to latency.update()

Null_Connection
--------
	No docstring found

Default values for newly created instances:

- timeout                  : 0
- memory_mode              : -1
- deleted                  : False
- ip                       : 
- add_on_init              : True
- memory_size              : 0
- blocking                 : 0
- socket_family            : 2
- as_port                  : 0
- connection_attempts      : 10
- added_to_network         : False
- network_packet_size      : 32768
- timeout_notify           : True
- target                   : ()
- verbosity                : 
- bind_on_init             : False
- socket_type              : 1
- _connecting              : False
- port                     : 80
- bad_target_verbosity     : 0
- auto_connect             : True
- network_buffer           : 
- closed                   : False

This object defines the following non-private methods:


- **on_connect**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.misc.securitylibrary.Null_Connection', class 'mpre.network.Tcp_Client', class 'mpre.network.Tcp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Process
--------

    Process objects represent activity that is run in a separate process

    The class is analagous to `threading.Thread`
    

Scanner
--------
	No docstring found

Default values for newly created instances:

- subnet                   : 127.0.0.1
- memory_mode              : -1
- deleted                  : False
- verbosity                : 
- priority                 : 0.04
- range                    : (0, 0, 0, 255)
- memory_size              : 4096
- auto_start               : True
- yield_interval           : 100
- ports                    : (22,)
- discovery_verbosity      : v

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **new_thread**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.misc.securitylibrary.Scanner', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Tcp_Port_Tester
--------
	No docstring found

Default values for newly created instances:

- as_port                  : 0
- closed                   : False
- memory_mode              : -1
- deleted                  : False
- ip                       : 
- add_on_init              : True
- memory_size              : 0
- socket_family            : 2
- port                     : 80
- connection_attempts      : 10
- target                   : ()
- network_packet_size      : 32768
- timeout_notify           : True
- added_to_network         : False
- verbosity                : 
- bind_on_init             : False
- socket_type              : 1
- _connecting              : False
- blocking                 : 0
- bad_target_verbosity     : 0
- auto_connect             : True
- network_buffer           : 
- timeout                  : 0

This object defines the following non-private methods:


- **on_connect**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.misc.securitylibrary.Tcp_Port_Tester', class 'mpre.network.Tcp_Client', class 'mpre.network.Tcp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


fork
--------
No documentation available