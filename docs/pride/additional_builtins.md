pride.additional_builtins
==============

 Additional builtin functions that are generally, frequently, and obviously useful.
    Functions defined here become available as builtins when pride is imported.
    Default builtins can be replaced by defining them here
    
    This module should only receive additions when absolutely necessary. 

RequestDenied
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.additional_builtins.RequestDenied'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

invoke
--------------

**invoke**(callable_string, *args, **kwargs):

		 Calls the method named in callable_string with args and kwargs.
     
        Base objects that are created via invoke instead of create will
        exist as a root object in the objects dictionary. 


raw_input
--------------

**raw_input**(prompt, must_reply):

		 raw_input function that plays nicely when sys.stdout is swapped.
            If must_reply equals True, then the prompt will be redisplayed
            until a non empty string is returned.
            
            For documentation of the standard CPython raw_input function, consult
            the python interpreter or the internet. 


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


restart
--------------

**restart**():

				No documentation available


shutdown
--------------

**shutdown**():

				No documentation available


slide
--------------

**slide**(iterable, x):

		 Yields x bytes at a time from iterable 


system_update
--------------

**system_update**():

				No documentation available
