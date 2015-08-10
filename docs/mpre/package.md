mpre.package
==============



Documentation
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'replace_reference_on_load': True,
	 'top_level_package': ''}

Method resolution order: 

	(<class 'mpre.package.Documentation'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **write_markdown_file**(self, markdown_text, filename):

				No documentation available


- **write_yml_entry**(self, entry, yml_file):

				No documentation available


Package
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'ignore_modules': (),
	 'include_documentation': False,
	 'include_source': True,
	 'package_name': None,
	 'python_extensions': ('.py', '.pyx', '.pyd', '.pso', '.so'),
	 'replace_reference_on_load': False,
	 'required_modules': (),
	 'required_packages': (),
	 'top_level_package': ''}

Method resolution order: 

	(<class 'mpre.package.Package'>, <class 'mpre.base.Base'>, <type 'object'>)

- **find_module**(self, module_name, path):

				No documentation available


- **load_module**(self, module_name):

				No documentation available


build_documentation_site
--------------

**build_documentation_site**(module):

				No documentation available


create_module
--------------

**create_module**(module_name, source, context):

		 Creates a module with the supplied name and source
