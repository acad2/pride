mpre.metapython
========
No documentation available

Instruction
--------
No documentation available

Metapython
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- keyboard_input           
- jython                   java -jar jython.jar
- prompt                   >>> 
- copyright                Type "help", "copyright", "credits" or "license" for more information.
- deleted                  False
- verbosity                
- traceback                <function format_exc at 0x01CB9B70>
- environment_setup        ['PYSDL2_DLL_PATH = C:\\Python27\\DLLs']
- priority                 0.04
- python                   python
- memory_size              4096
- network_buffer           
- auto_start               True
- implementation           python
- interface                0.0.0.0
- command                  shell_launcher.py
- pypy                     pypy
- port                     40022
- authentication_scheme    networklibrary.Basic_Authentication

This object defines the following non-private methods:


- **setup_environment**(self):

		  No documentation available



- **run**(self):

		  No documentation available



- **start_metapython**(self):

		  No documentation available



- **handle_login_success**(self, connection):

		  No documentation available



- **handle_logins**(self):

		  No documentation available



- **exit**(self, exit_code=0):

		  No documentation available



- **execute_code**(self, connection, code):

		  No documentation available


This objects method resolution order is:

(class 'mpre.metapython.Metapython', class 'mpre.vmlibrary.Process', class 'mpre.base.Base', type 'object')


Shell
--------
	(Potentially remote) connection to the interactive Metapython

Default values for newly created instances:

- network_packet_size      4096
- keyboard_input           
- startup_definitions      
- username                 root
- copyright                Type "help", "copyright", "credits" or "license" for more information.
- deleted                  False
- ip                       localhost
- verbosity                
- traceback                <function format_exc at 0x01CB9B70>
- auto_login               True
- priority                 0.04
- memory_size              4096
- network_buffer           
- auto_start               False
- prompt                   >>> 
- password                 password
- port                     40022

This object defines the following non-private methods:


- **run**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.metapython.Shell', class 'mpre.vmlibrary.Process', class 'mpre.base.Base', type 'object')


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

    