mpre.persistence
==============



CorruptPickleError
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.errors.CorruptPickleError'>,
	 <class 'pickle.UnpicklingError'>,
	 <class 'pickle.PickleError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

authenticated_dump
--------------

**authenticated_dump**(py_object, secret_key, _file, hash_algorithm):

		 usage: authenticated_dump(py_object, secret_key, _file=None, 
                                  hash_algorithm=hashlib.sha512) => authenticated_bytestream
                                  
        Saves a python object via pickle. A message authentication code is generated and
        prepended to the bytestream via HMAC(secret_key, bytestream, hash_algorithm).hexdigest() + bytestream.
        If _file is supplied, the bytestream will be written to the file and not returned (as in pickle.dump),
        if _file is omitted, the authenticated bytestream will be returned (as in pickle.dumps)


authenticated_load
--------------

**authenticated_load**(bytestream, secret_key, hash_algorithm):

		 usage: authenticated_load(bytestream, secret_key, 
                                  hash_algorithm=hashlib.sha512) => py_object
                                  
        Returns a python object from a bytestream.
        The secret_key must be the same key used to create the bytestream. 
        bytestream may be either a file like object or a bytestring as retuned
        by authenticated_dump. if bytestream is a file, a byte string will be
        obtained via calling file.read().


create_module
--------------

**create_module**(module_name, source, context):

		 Creates a module with the supplied name and source


load
--------------

**load**(attributes, _file):

		 usage: load([attributes], [_file]) => restored_instance, attributes
    
        Loads state preserved by the persistence.save method. Loads an instance from either
        a bytestream or file, as returned by the save method.


save
--------------

**save**(self, attributes, _file):

		 usage: base.save([attributes], [_file])
        
        Saves the state of the calling objects __dict__. If _file is not specified,
        a pickled stream is returned. If _file is specified, the stream is written
        to the supplied file like object via pickle.dump.
        
        The attributes argument, if specified, should be a dictionary containing 
        the attribute:value pairs to be pickled instead of the objects __dict__.
        
        If the calling object is one that has been created via the update method, the 
        returned state will include any required source code to rebuild the object.


save_function
--------------

**save_function**(function):

				No documentation available
