pride.contextmanagers
==============



backup
--------------

**backup**(args, **kwds):

				No documentation available


current_working_directory
--------------

**current_working_directory**(args, **kwds):

		 Temporarily sets the current working directory 


file_contents_swapped
--------------

**file_contents_swapped**(args, **kwds):

		 Enters a context where the data of the supplied file/filepath are the 
        contents specified in the contents argument. After exiting the context,
        the contents are replaced.
        
        Note that if a catastrophe like a power outage occurs, pythons context 
        manager may not be enough to restore the original file contents. 


inplace_swap
--------------

**inplace_swap**(args, **kwds):

				No documentation available
