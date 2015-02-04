mpre.misc.securitylibrary
========
No documentation available

DoS
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- keyboard_input           
- display_progress         False
- salvo_size               100
- timeout_notify           False
- deleted                  False
- ip                       localhost
- verbosity                
- count                    0
- priority                 0.04
- memory_size              4096
- network_buffer           
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

(class 'mpre.misc.securitylibrary.DoS', class 'mpre.vmlibrary.Process', class 'mpre.base.Base', type 'object')


Instruction
--------
No documentation available

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
- keyboard_input           
- scan_size                1
- subnet                   127.0.0.1
- deleted                  False
- verbosity                
- timeout                  0
- priority                 0.04
- range                    (0, 0, 0, 254)
- memory_size              4096
- network_buffer           
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

(class 'mpre.misc.securitylibrary.Scanner', class 'mpre.vmlibrary.Process', class 'mpre.base.Base', type 'object')
