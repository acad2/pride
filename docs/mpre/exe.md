mpre.exe
==============

 Provides simple utilities for creating cython + gcc compiled 
    executables from python modules. 

Executable
--------------

	 Used to make a cython gcc compiled executable from a python module. 


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'file': None,
	 'filename': 'metapython.exe',
	 'loader_type': 'mpre.exe.Loader',
	 'main_source': '',
	 'package': None,
	 'replace_reference_on_load': True,
	 'use_unicode_literals': True}

Method resolution order: 

	(<class 'mpre.exe.Executable'>, <class 'mpre.base.Base'>, <type 'object'>)

- **build**(self):

		 Builds the executable source in python and compiles it
            via cython and gcc. 


Loader
--------------

	 Used to customize the define bootstrap process. 


Instance defaults: 

	{'_deleted': False,
	 'definitions': ('mpre.persistence.authenticated_load',
	                 'mpre.persistence.load',
	                 'mpre.base.load',
	                 'mpre.errors.CorruptPickleError',
	                 'mpre.module_utilities.create_module'),
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'importer': '',
	 'replace_reference_on_load': True,
	 'required_imports': ('sys',
	                      'hashlib',
	                      'pickle',
	                      'importlib',
	                      'types',
	                      'hmac',
	                      'binascii'),
	 'variables': {'ASCIIKEY': 'mpre.persistence.ASCIIKEY'}}

Method resolution order: 

	(<class 'mpre.exe.Loader'>, <class 'mpre.base.Base'>, <type 'object'>)

- **build**(self):

				No documentation available
