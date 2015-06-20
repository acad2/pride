mpre.exe
==============



Executable
--------------

	No docstring found


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
	 'use_unicode_literals': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.exe.Executable'>, <class 'mpre.base.Base'>, <type 'object'>)

- **build**(self):

				No documentation available


Loader
--------------

	No docstring found


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
	 'variables': {'ASCIIKEY': 'mpre.persistence.ASCIIKEY'},
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.exe.Loader'>, <class 'mpre.base.Base'>, <type 'object'>)

- **build**(self):

				No documentation available
