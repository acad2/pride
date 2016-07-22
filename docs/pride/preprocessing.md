pride.preprocessing
==============



Compiler
--------------

	 Compiles python source to bytecode. Source may be preprocessed.
        This object is automatically instantiated and inserted into
        sys.meta_path as the first entry when pride is imported.

        Preprocessed source is stored in a file on disk. This is done via the
        anydbm module, which doesn't offer the same consistency of data as a 
        proper database. The cache can become corrupted and must be deleted, 
        Caching is a performance optimization and not functionality critical. 


Method resolution order: 

	(<class 'pride.preprocessing.Compiler'>, <type 'object'>)

- **load_module**(self, module_name):

				No documentation available


- **find_module**(self, module_name, path):

				No documentation available


- **compile_module**(self, module_name, source, path):

				No documentation available


- **compile**(self, source, filename):

				No documentation available


- **reload_module**(self, module_name):

				No documentation available


- **preprocess**(self, source):

				No documentation available


Export_Keyword
--------------

	 Enables the keyword syntax:
        
        export module_name to fully.qualified.domain.name [as name]
        
        Executes the module specified by module name on the remote host running
        at the address obtained by socket.gethostbyname(fully.qualified.domain.name).
        The remote host must be running pride, the network must be configured
        appropriately, and a Shell connection must be made beforehand. 
        
        If the optional as clause is included, the module will be saved 
        under the name specified instead of ran. 


Method resolution order: 

	(<class 'pride.preprocessing.Export_Keyword'>,
	 <class 'pride.preprocessing.Keyword'>,
	 <class 'pride.preprocessing.Preprocessor'>,
	 <type 'object'>)

Keyword
--------------

	 Base class for new keywords. Subclasses should specify a keyword_string
        class attribute. Keyword functionality is defined in pride.keywords. 


Method resolution order: 

	(<class 'pride.preprocessing.Keyword'>,
	 <class 'pride.preprocessing.Preprocessor'>,
	 <type 'object'>)

- **handle_source**(_class, source):

				No documentation available


Parser
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.preprocessing.Parser'>, <type 'object'>)

- **extract_code**(source):

		 Returns source without header, comments, or docstring. 


- **remove_header**(source):

		 Returns source without a class or def header. 


- **get_string_indices**(source):

		 Return a list of indices of strings found in source. 
            Includes substrings located within other strings. 


- **remove_comments**(source):

				No documentation available


- **find_symbol**(symbol, source, back_delimit, forward_delimit, start_index, quantity):

		 Locates all occurrences of symbol inside source up to the given
            quantity of times. Matches only count if the symbol is not inside
            a quote or behind a comment. 


- **replace_symbol**(symbol, source, replacement, back_delimit, forward_delimit, start_index):

				No documentation available


- **remove_docstring**(source):

		 Returns source without docstring 


Preprocess_Decorator
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.preprocessing.Preprocess_Decorator'>,
	 <class 'pride.preprocessing.Preprocessor'>,
	 <type 'object'>)

- **handle_source**(_class, source):

				No documentation available


Preprocessor
--------------

	 Base class for establishing interface of preprocessor objects 


Method resolution order: 

	(<class 'pride.preprocessing.Preprocessor'>, <type 'object'>)

- **handle_source**(_class, source):

				No documentation available


find_unquoted_symbol
--------------

**find_unquoted_symbol**(symbol, data):

				No documentation available


resolve_string
--------------

**resolve_string**(module_name):

		Given a string of a.b...z, return the object z, importing 
       any required packages and modules to access z.
       
       Alternatively, resolves a reference from the objects dictionary, and 
       potentially loads a specified attribute i.e.:
        
        resolve_string("/Python") == objects["/Python"]
        resolve_string("/User/Shell.logged_in") == objects["/User/Shell"].logged_in
        
       Can also be used to import modules:
        
        resolve_string("audioop")
        
       Put simply: given a string that points to an object, module, or 
       attribute, return the object, module, or attribute specified. 
