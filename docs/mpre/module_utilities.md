mpre.module_utilities
==============



create_module
--------------

**create_module**(module_name, source, context):

		 Creates a module with the supplied name and source


get_module_source
--------------

**get_module_source**(module):

				No documentation available


get_required_modules
--------------

**get_required_modules**(module):

				No documentation available


get_required_sources
--------------

**get_required_sources**(modules):

				No documentation available


modules_preserved
--------------

**modules_preserved**(, *args, **kwds):

		 Enter a context where the modules specified will be backed up + restored upon exit


modules_switched
--------------

**modules_switched**(, *args, **kwds):

		 Enters a context where the modules in module_dict.keys are replaced by the source
        specified in module_dict[key]. The original modules will be restored upon exit.


reload_module
--------------

**reload_module**(module_name):

		 Reloads the module specified by module_name
