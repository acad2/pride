import hashlib
import pickle
import importlib
import hmac

import mpre.module_utilities as module_utilities
from mpre.errors import CorruptPickleError

ASCIIKEY = ''.join(chr(x) for x in xrange(256))#os.urandom(512)

def authenticated_dump(py_object, secret_key, _file=None,  hash_algorithm=hashlib.sha512):
    """ usage: authenticated_dump(py_object, secret_key, _file=None, 
                                  hash_algorithm=hashlib.sha512) => authenticated_bytestream
                                  
        Saves a python object via pickle. A message authentication code is generated and
        prepended to the bytestream via HMAC(secret_key, bytestream, hash_algorithm).hexdigest() + bytestream.
        If _file is supplied, the bytestream will be written to the file and not returned (as in pickle.dump),
        if _file is omitted, the authenticated bytestream will be returned (as in pickle.dumps)"""
    bytestream = pickle.dumps(py_object)
    result = hmac.HMAC(secret_key, bytestream, hash_algorithm).hexdigest() + bytestream
    if _file:
        _file.write(result)
    else:
        return result

def authenticated_load(bytestream, secret_key, hash_algorithm=hashlib.sha512):
    """ usage: authenticated_load(bytestream, secret_key, 
                                  hash_algorithm=hashlib.sha512) => py_object
                                  
        Returns a python object from a bytestream.
        The secret_key must be the same key used to create the bytestream. 
        bytestream may be either a file like object or a bytestring as retuned
        by authenticated_dump. if bytestream is a file, a byte string will be
        obtained via calling file.read()."""  
    if hasattr(bytestream, 'read'):
        bytestream = bytestream.read()
        
    mac_size = hash_algorithm().digestsize * 2
    try:
        pickled_object = bytestream[mac_size:]
    except TypeError:
        bytestream = bytestream.read()
        pickled_object = bytestream[mac_size:]
    valid = hmac.compare_digest(bytestream[:mac_size], 
                                hmac.HMAC(secret_key, pickled_object, hash_algorithm).hexdigest())
    if valid:
        return pickle.loads(pickled_object)
    else:
        raise CorruptPickleError("Message authentication code mismatch\n\n" + bytestream[:mac_size])

def save(self, attributes=None, _file=None):
    """ usage: base.save([attributes], [_file])
        
        Saves the state of the calling objects __dict__. If _file is not specified,
        a pickled stream is returned. If _file is specified, the stream is written
        to the supplied file like object via pickle.dump.
        
        The attributes argument, if specified, should be a dictionary containing 
        the attribute:value pairs to be pickled instead of the objects __dict__.
        
        If the calling object is one that has been created via the update method, the 
        returned state will include any required source code to rebuild the object."""
    if not attributes:
        try:
            attributes = self.__getstate__()
        except AttributeError:
            attributes = self.__dict__
    else:
        attributes = attributes.copy() # avoid mutation in case it was passed in via interpreter session
        
    if "_required_modules" in attributes: # modules are not pickle-able
        module_info = attributes.pop("_required_modules")
        attributes["_required_modules"] = modules = []
        for name, source, module in module_info[:-1]:
            modules.append((name, source, None))
        modules.append(module_info[-1])
    else:
        attributes["_required_module"] = (self.__module__, self.__class__.__name__)
    
    saved = authenticated_dump(attributes, ASCIIKEY)
    
    if _file:
        _file.write(saved)
    else:
        return saved
    
def load(attributes=None, _file=None):
    """ usage: load([attributes], [_file]) => restored_instance
    
        Loads state preserved by the save method. Loads an instance from either
        a bytestream or file, as returned by the save method..
        
        To customize the behavior of an object after it has been loaded, one should
        extend the on_load method.""" 
    if _file:
        assert not attributes
        attributes = _file.read()  
    elif not attributes:
        raise ValueError("No attributes bytestream or file object supplied to load")
    attributes = authenticated_load(attributes, ASCIIKEY)   
    
    if "_required_modules" in attributes:
        _required_modules = []
        incomplete_modules = attributes["_required_modules"]
        class_name = incomplete_modules.pop()
        module_sources = dict((module_name, source) for module_name, source, none in 
                              incomplete_modules)

        for module_name, source, none in incomplete_modules:
            module = module_utilities.create_module(module_name, source)
            _required_modules.append((module_name, source, module))       
        
        self_class = getattr(module, class_name)
        attributes["_required_modules"] = _required_modules        
    else:
        module_name, class_name = attributes["_required_module"]
        module = importlib.import_module(module_name)
        self_class = getattr(module, class_name)            
    self = self_class.__new__(self_class)
    return self, attributes