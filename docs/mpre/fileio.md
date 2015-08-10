mpre.fileio
==============

 Provides objects for file related tasks 

Cached
--------------

	 A memoization decorator that should work with any method and argument structure


Method resolution order: 

	(<class 'mpre.fileio.Cached'>, <type 'object'>)

- **decrement_handle**(self, key):

				No documentation available


File
--------------

	 usage: File(path='', mode='', 
                    file=None, file_type='file', **kwargs) => file
    
        Return a wrapper around a file like object. File objects can be
        saved and loaded. The files contents will be maintained if
        persistent is True, which is the default.
        The wrapped file can be specified by the file argument. 
        If the file argument is not present, a file like object will
        be opened and wrapped. The type may be specified by the file_type
        attribute. The default is a regular file, which will require
        an appropriate path and mode to be specified when initializing. 


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'file': None,
	 'file_type': 'file',
	 'mode': '',
	 'persistent': True,
	 'replace_reference_on_load': True,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'mpre.fileio.File'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_load**(self, attributes):

				No documentation available


- **delete**(self):

				No documentation available


Mmap
--------------

	Usage: mmap [offset] = fileio.Mmap(filename, 
                                          file_position_or_size=0,
                                          blocks=0)
                                 
        Return an mmap.mmap object. Use of this class presumes a
        need for a slice into a potentially large file at an arbitrary
        point without loading the entire file contents. These slices
        are cached so that further requests for the same chunk will return the same mmap.
        
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
            


Method resolution order: 

	(<class 'mpre.fileio.Mmap'>, <type 'object'>)

- 

current_working_directory
--------------

**current_working_directory**(, *args, **kwds):

		 Temporarily sets the current working directory 


ensure_file_exists
--------------

**ensure_file_exists**(filepath, data):

		usage: ensure_file_exists(filepath, [data=''])
        
        filepath is the absolute or relative path of the file.
        If the file does not exist, it is created
        
        data is optional. if specified, the file will be truncated and 
        the data will written to the file. The file contents will be
        nothing but the specified data


ensure_folder_exists
--------------

**ensure_folder_exists**(pathname, file_system):

		usage: ensure_folder_exists(pathname)
    
       If the named folder does not exist, it is created


file_contents_swapped
--------------

**file_contents_swapped**(, *args, **kwds):

		 Enters a context where the data of the supplied file/filepath are the 
        contents specified in the contents argument.
