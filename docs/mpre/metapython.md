mpre.metapython
========
No documentation available

Instruction
--------
No documentation available

Interpreter_Client
--------
	No docstring found

Default values for newly created instances:

- username                 ellaphant
- deleted                  False
- startup_definitions      
- add_on_init              True
- resend_interval          0.2
- allow_port_zero          True
- memory_size              32768
- interface                0.0.0.0
- password                 puppydog
- blocking                 0
- network_packet_size      32768
- target                   (u'localhost', 40022)
- timeout_after            0
- resend_limit             10
- verbosity                
- port                     0
- idle                     True
- network_buffer           
- timeout                  0
- email                    notneeded@no.com

This object defines the following non-private methods:


- **login_result**(self, sender, packet):

		  No documentation available



- **exec_code_request**(self, sender, source):

		  No documentation available



- **result**(self, sender, packet):

		  No documentation available



- **execute_source**(self, source):

		  No documentation available


This objects method resolution order is:

(class 'mpre.metapython.Interpreter_Client', class 'mpre.network2.Authenticated_Client', class 'mpre.network2.Service', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Interpreter_Service
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      32768
- database_filename        :memory:
- copyright                Type "help", "copyright", "credits" or "license" for more information.
- timeout_after            0
- deleted                  False
- resend_limit             10
- verbosity                
- add_on_init              True
- resend_interval          0.2
- idle                     True
- allow_port_zero          True
- memory_size              32768
- network_buffer           
- timeout                  0
- blocking                 0
- interface                0.0.0.0
- login_message            login success
- port                     40022

This object defines the following non-private methods:


- **exec_code**(instance, sender, packet):

		  No documentation available



- **login**(self, sender, packet):

		  No documentation available


This objects method resolution order is:

(class 'mpre.metapython.Interpreter_Service', class 'mpre.network2.Authenticated_Service', class 'mpre.network2.Service', class 'mpre.network.Udp_Socket', class 'mpre.network.Socket', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Metapython
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- keyboard_input           
- interpreter_enabled      True
- prompt                   >>> 
- copyright                Type "help", "copyright", "credits" or "license" for more information.
- deleted                  False
- verbosity                
- environment_setup        ['PYSDL2_DLL_PATH = C:\\Python27\\DLLs']
- priority                 0.04
- implementation           python
- memory_size              4096
- network_buffer           
- auto_start               True
- interface                0.0.0.0
- command                  shell_launcher.py
- port                     40022

This object defines the following non-private methods:


- **setup_environment**(self):

		  No documentation available



- **start_service**(self):

		  No documentation available



- **start_machine**(self):

		  No documentation available



- **exit**(self, exit_code=0):

		  No documentation available



- **exec_command**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.metapython.Metapython', class 'mpre.base.Base', type 'object')


Shell
--------
	Captures user input and passes it to Interpreter_Client

Default values for newly created instances:

- network_packet_size      4096
- keyboard_input           
- username                 root
- copyright                Type "help", "copyright", "credits" or "license" for more information.
- deleted                  False
- ip                       localhost
- verbosity                
- startup_definitions      
- priority                 0.04
- memory_size              4096
- network_buffer           
- auto_start               False
- prompt                   >>> 
- password                 password
- port                     40022

This object defines the following non-private methods:


- **handle_keystrokes**(self, sender, keyboard_input):

		  No documentation available


This objects method resolution order is:

(class 'mpre.metapython.Shell', class 'mpre.base.Base', type 'object')


closing
--------
Context to automatically close something at the end of a block.

    Code like this:

        with closing(<module>.open(<arguments>)) as f:
            <block>

    is equivalent to this:

        f = <module>.open(<arguments>)
        try:
            <block>
        finally:
            f.close()

    