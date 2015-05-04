mpre.fileio
==============



Cached
--------------

	 A memoization decorator that should work with any method and argument structure


Method resolution order: 

	(<class 'mpre.fileio.Cached'>, <type 'object'>)

- **decrement_handle**(self, key):

		No documentation available


Directory
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'directory': None,
	 'file_system': 'disk',
	 'is_directory': True,
	 'path': '',
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.fileio.Directory'>, <class 'mpre.base.Base'>, <type 'object'>)

- **delete**(self):

		No documentation available


Encrypted_File
--------------

	 usage: Encrypted_File(_file, **kwargs) => encrypted_file
               
        Returns an Encrypted_File object. Calls to the write method will be encrypted with
        encrypted_file.key (currently via the mpre.utilities.convert function), and reads will be decrypted using the same key. Currently only supports ascii. Should currently
        be considered as a demonstartion only, please do not depend upon this to keep
        information private.
        
        The key is only valid for as long as the instance exists. In order to preserve
        the key, utilize the save method. The resulting pickle stream can later be
        unpickled and supplied to the load method to recover the original instance with 
        the appropriate key to decrypt the file.


Instance defaults: 

	{'_deleted': False,
	 'block_size': 1024,
	 'directory': None,
	 'file': None,
	 'file_system': 'disk',
	 'file_type': 'StringIO.StringIO',
	 'is_directory': False,
	 'mode': '',
	 'path': '',
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.fileio.Encrypted_File'>,
	 <class 'mpre.fileio.File'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **truncate**(self, size):

		No documentation available


- **decrypt**(self, data):

		No documentation available


- **derive_key**(self):

		No documentation available


- **encrypt**(self, data):

		No documentation available


- **write**(self, data):

		No documentation available


- **read**(self, size):

		No documentation available


File
--------------

	 usage: File(filename='', mode='', file=None, file_system="disk", **kwargs) => file
    
        Return a wrapper around a file like object. File objects are pickleable. 
        Upon pickling the files data will be saved and upon loading the data restored. 
        The default is False. The wrapped file can be specified by the file argument. If
        the file argument is not present, the file named in filename will be opened in the
        specified mode.


Instance defaults: 

	{'_deleted': False,
	 'directory': None,
	 'file': None,
	 'file_system': 'disk',
	 'file_type': 'StringIO.StringIO',
	 'is_directory': False,
	 'mode': '',
	 'path': '',
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.fileio.File'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_load**(self, attributes):

		No documentation available


- **delete**(self):

		No documentation available


File_System
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'auto_start': False,
	 'file_systems': ('disk', 'virtual'),
	 'priority': 0.04,
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.fileio.File_System'>, <class 'mpre.base.Base'>, <type 'object'>)

- **listdir**(self, path):

		No documentation available


- **getcwd**(self, file_system):

		No documentation available


- **new_file_system**(self, file_system):

		No documentation available


- **join**(self, path_one, path_two):

		No documentation available


- **exists**(self, path, file_type):

		No documentation available


- **change_directory**(self, path):

		No documentation available


- **change_file_system**(self, file_system):

		No documentation available


- **remove**(self, _file, file_system):

		No documentation available


- **get_file**(self, path):

		No documentation available


- **add**(self, _file):

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

- **new_mmap**(filename, file_position, blocks):

		No documentation available


closing
--------------

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

    


Method resolution order: 

	(<class 'contextlib.closing'>, <type 'object'>)

- **contextmanager**(func):

		@contextmanager decorator.

    Typical usage:

        @contextmanager
        def some_generator(<arguments>):
            <setup>
            try:
                yield <value>
            finally:
                <cleanup>

    This makes this:

        with some_generator(<arguments>) as <variable>:
            <body>

    equivalent to this:

        <setup>
        try:
            <variable> = <value>
            <body>
        finally:
            <cleanup>

    


- **ensure_file_exists**(filepath, data):

		usage: ensure_file_exists(filepath, [data=('a', '')])
        
        filepath is the absolute or relative path of the file.
        If the file does not exist, it is created
        
        data is optional. if specified, data[0] = mode and 
        data[1] = the data to be written
        
        mode should be 'a' or 'w', 'a' is the default. 
        'w' will truncate the file and the only contents
        will be the data supplied in data[1]


- **ensure_folder_exists**(pathname, file_system):

		usage: ensure_folder_exists(pathname)
    
       If the named folder does not exist, it is created


- **file_contents_swapped**(, *args, **kwds):

		 Enters a context where the data of the supplied file/filepath are the 
        contents specified in the contents argument.
