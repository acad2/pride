mpre.misc.securitylibrary
========
No documentation available

DoS
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- count                    0
- display_progress         False
- salvo_size               100
- timeout_notify           False
- deleted                  False
- ip                       localhost
- verbosity                
- priority                 0.04
- memory_size              4096
- auto_start               True
- display_latency          False
- port                     80
- target                   None

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **socket_recv**(self, connection):

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
        that they do not happen inline, even if priority is 0.0. 
        Because they do not execute in the current scope, the return value 
        from the method call is not available through this mechanism.

Latency
--------
No documentation available

Process
--------

    Process objects represent activity that is run in a separate process

    The class is analagous to `threading.Thread`
    

Scanner
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- subnet                   127.0.0.1
- scan_size                1
- deleted                  False
- verbosity                
- timeout                  0
- priority                 0.04
- range                    (0, 0, 0, 254)
- memory_size              4096
- auto_start               True
- yield_interval           50
- ports                    (22,)

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **scan_address**(self, address, ports):

		  No documentation available



- **create_threads**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.misc.securitylibrary.Scanner', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')
