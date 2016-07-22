pride.module_utilities
==============



create_module
--------------

**create_module**(module_name, source, context):

		 Creates a module with the supplied name and source


get_all_modules_for_class
--------------

**get_all_modules_for_class**(_class):

				No documentation available


get_module_source
--------------

**get_module_source**(module):

		 Retrieve the source code of module. If the source code has been
        processed by the pride compiler, the preprocessed code is returned
        from the compilers cache. Otherwise, the inspect module is used. 


get_required_modules
--------------

**get_required_modules**(module):

				No documentation available


get_required_sources
--------------

**get_required_sources**(modules):

				No documentation available


installed_modules
--------------

**installed_modules**(directories):

		 Returns a list of the names of available python modules 


modules_preserved
--------------

**modules_preserved**(args, **kwds):

		 Enter a context where the modules specified will be backed up + restored upon exit
        If modules is not specified, all modules in sys.modules are backed up and resotred. 


modules_switched
--------------

**modules_switched**(args, **kwds):

		 Enters a context where the modules named in module_dict keys are 
        recompiled and replaced by the associated source. The original 
        modules will be restored upon exit. 


reload_module
--------------

**reload_module**(module_name):

		 Reloads the module specified by module_name
