pride.patch
==============

 pride.patch - utilities for patching python standard library modules
    Patches named in pride.patch.patches will automatically be instantiated
    when pride is imported. 

Patched_Module
--------------

	 The base class for patching modules 


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'module_name': '',
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': (),
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.patch.Patched_Module'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

Stdout
--------------

	No docstring found


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'file': None,
	 'limit_log_size': 1048576,
	 'log_type': 'StringIO.StringIO',
	 'logging_enabled': True,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.patch.Stdout'>, <class 'pride.base.Base'>, <type 'object'>)

- **switched**(args, **kwds):

				No documentation available


- **flush**(self):

				No documentation available


- **write**(self, data):

				No documentation available


inspect
--------------

	No docstring found


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'module_name': 'inspect',
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': (),
	 'wrapped_object': None}

Method resolution order: 

	(<class 'pride.patch.inspect'>,
	 <class 'pride.patch.Patched_Module'>,
	 <class 'pride.base.Wrapper'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **get_source**(_object):

				No documentation available
