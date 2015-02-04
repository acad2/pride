mpre.misc.mmaptest
========
No documentation available

File
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- deleted                  False
- verbosity                
- memory_size              4096

This object defines the following non-private methods:


- **delete**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.misc.mmaptest.File', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


IO_Manager
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- keyboard_input           
- total_mmap_blocks_allowed50
- deleted                  False
- verbosity                
- priority                 0.04
- memory_size              4096
- network_buffer           
- auto_start               True
- max_blocks_per_mmap      5

This object defines the following non-private methods:


- **load_mmap**(self, filename, start_index, blocks=0):

		  No documentation available



- **delete**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.misc.mmaptest.IO_Manager', class 'mpre.vmlibrary.Process', class 'mpre.base.Base', type 'object')


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

    