pride.fileio
==============

 Provides objects for file related tasks 

Cached
--------------

	 A memoization decorator that should work with any method and argument structure


Method resolution order: 

	(<class 'pride.fileio.Cached'>, <type 'object'>)

- **decrement_handle**(self, key):

				No documentation available


Database_File
--------------

	 A file that persists in the /Python/File_System when saved or flushed.
        Standard read/write/seek operations take place with a file like object
        of type file_type. Data is manipulated in memory and is only saved to the 
        database when flush or save is called. 
        
        tags may be specified as an iterable of strings describing the 
        contents or purpose of the file. Files in the file system can be
        searched by tag. Tags may be modified whenever required by assigning
        them when creating the file.
        
        The encrypted flag determines whether or not to encrypt file data
        stored in the file system database. Only file data is encrypted, not
        metadata or file name. Data is encrypted using pride.security.encrypt,
        which defaults to AES-GCM with a 16 byte random salt. The encryption
        key is that of the currently logged in User; If no User is logged in,
        files cannot be encrypted or decrypted. The encrypt flag only applies
        to memory saved onto the file system database; The contents of memory
        are not encrypted. 


Instance defaults: 

	{'_data': '',
	 'deleted': False,
	 'dont_save': False,
	 'encrypted': False,
	 'file': None,
	 'file_type': 'StringIO.StringIO',
	 'indexable': True,
	 'mode': '',
	 'parse_args': False,
	 'persistent': True,
	 'replace_reference_on_load': True,
	 'startup_components': (),
	 'tags': '',
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.fileio.Database_File'>,
	 <class 'pride.fileio.File'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **flush**(self):

				No documentation available


- **close**(self):

				No documentation available


- **save**(self):

		 Saves file contents and metadata to /Python-File_System. 


- **delete_from_filesystem**(self):

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

	{'deleted': False,
	 'dont_save': False,
	 'file': None,
	 'file_type': 'file',
	 'mode': '',
	 'parse_args': False,
	 'persistent': True,
	 'replace_reference_on_load': True,
	 'startup_components': (),
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.fileio.File'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **truncate**(self, size):

				No documentation available


- **on_load**(self, attributes):

				No documentation available


- **write**(self, data):

				No documentation available


- **delete_from_filesystem**(self):

				No documentation available


- **delete**(self):

				No documentation available


File_Attributes
--------------

	No docstring found


Instance defaults: 

	{'attributes': ('protection_bits',
	                'inode_number',
	                'device',
	                'number_of_hard_links',
	                'owner_user_id',
	                'owner_group_id',
	                'file_size',
	                'last_accessed',
	                'last_modified',
	                'metadata_last_modified',
	                'time_created'),
	 'deleted': False,
	 'dont_save': False,
	 'filename': '',
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.fileio.File_Attributes'>,
	 <class 'pride.base.Adapter'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

File_System
--------------

	 Database object for managing database file objects. 


Instance defaults: 

	{'auto_commit': True,
	 'connection': None,
	 'cursor': None,
	 'database_name': '',
	 'deleted': False,
	 'detect_types_flags': 1,
	 'dont_save': False,
	 'hash_function': 'SHA256',
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'return_cursor': False,
	 'salt_size': 16,
	 'startup_components': (),
	 'text_factory': <type 'str'>,
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.fileio.File_System'>,
	 <class 'pride.database.Database'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **delete_file**(self, filename):

				No documentation available


- **open_file**(self, filename, mode):

				No documentation available


- **save_file**(self, filename, data, tags, encrypt, indexable):

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

	(<class 'pride.fileio.Mmap'>, <type 'object'>)

- 

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
