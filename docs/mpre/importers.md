mpre.importers
==============

 Contains import related functions and objects, including the compiler 

Compiler
--------------

	 Compiles python source to bytecode. Source may be preprocessed.
        This object is automatically instantiated and inserted into
        sys.meta_path as the first entry. 


Method resolution order: 

	(<class 'mpre.importers.Compiler'>, <type 'object'>)

- **load_module**(self, module_name):

				No documentation available


- **find_module**(self, module_name, path):

				No documentation available


- **compile_source**(self, source, filename):

				No documentation available


- **compile_module**(self, module_name, source, path):

				No documentation available


- **preprocess**(self, source):

				No documentation available


Dollar_Sign_Directive
--------------

	 Replaces '$' directive with mpre.objects lookup. This
        facilitates the syntatic sugar $Component, which is
        translated to mpre.objects['Component']. 


Method resolution order: 

	(<class 'mpre.importers.Dollar_Sign_Directive'>, <type 'object'>)

- **handle_input**(self, source):

				No documentation available


From_Disk
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.importers.From_Disk'>, <type 'object'>)

- **find_module**(self, module_name, path):

				No documentation available


- **load_module**(self, module_name):

				No documentation available


imports_from_disk
--------------

**imports_from_disk**(, *args, **kwds):

				No documentation available


sys_meta_path_switched
--------------

**sys_meta_path_switched**(, *args, **kwds):

				No documentation available
