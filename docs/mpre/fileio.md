mpre.fileio
========
No documentation available

Cached
--------
No documentation available

File
--------
	usage: file_object = File([filename], [mode], [file])
	
	   Creates a File object. File objects are pickleable and
	   support the reactor interface for reading/writing to the
	   underlying wrapped file.

Default values for newly created instances:

- memory_size              4096
- memory_mode              -1
- update_flag              False
- deleted                  False
- verbosity                
- storage_mode             dont_copy

This object defines the following non-private methods:


- **handle_write**(self, sender, packet):

		  No documentation available



- **handle_read**(self, sender, packet):

		  No documentation available


This objects method resolution order is:

(class 'mpre.fileio.File', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Mmap
--------
Usage: mmap [offset] = fileio.Mmap(filename, 
                                          file_position_or_size=0,
                                          blocks=0)
                                 
        Return an mmap.mmap object. Use of this class presumes a
        need for a slice into a potentially large file at an arbitrary
        point without loading the entire file contents. These slices
        are cached, and the size of the cache may be altered.
        
            - if filename is -1 (a chunk of anonymous memory), then no 
              offset is returned. the second argument is interpreted
              as the desired size of the chunk of memory.
            - if filename is specified, the second argument is
              interpreted as the index into the file the slice
              should be opened to.
            
            The default value for the second argument is 0, which will
            open a slice at the beginning of the specified file
            
            - the blocks argument may be specified to request the
              mapping to be of size (blocks * mmap.ALLOCATIONGRANULARITY)
            - this argument has no effect when used with -1 for the filename
            
            

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

    