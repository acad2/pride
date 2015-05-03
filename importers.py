import inspect
import sys
import importlib
import contextlib
import mpre.utilities as utilities
    
@contextlib.contextmanager
def sys_meta_path_switched(new_meta_path):
    backup = sys.meta_path
    sys.meta_path = new_meta_path
    try:
        yield
    finally:
        sys.meta_path = backup
        

class Required_Modules(object):
    
    def __init__(self, _object):
        self.required_modules = []
        self.source = {}
        self._object = _object
      #  self.get_modules(_object)
            
    def get_modules(self, _object):
        if hasattr(_object, "__module__"):
            module_name = _object.__module__
            module = sys.objects[module_name]
        else:
            module = _object
            module_name = module.__name__
            
        source = inspect.getsource(module)
        with module_utilities.modules_preserved([key for key, value in sys.modules.items() if value]):
            sys.modules = {}
            with sys_meta_path_switched((self, )):
                assert not sys.modules
                __import__(module_name)
                #_module = importlib.import_module(module_name)
                #_module = module_utilities.create_module(module_name, source) 
        
    def find_module(self, module_path, path=None):
        print "Finding module: ", module_path
        self.required_modules.append(module_path)
        return self
        
    def load_module(self, module_path):
        module = importlib.import_module(module_path)
        try:
            source = inspect.getsource(module)
        except TypeError: # is a builtin
            source = ''
        self.source[module_path] = source
        
        
class From_Disk_Importer(object):
        
    def __init__(self, modules=tuple()):
        self.modules = modules
        
    def find_module(self, module_name, path):
        if not self.modules or module_name in self.modules:
            return self
        return None
        
    def load_module(self, module_name):
        module = (sys.modules[module_name] if module_name in sys.modules else
                  importlib.import_module(module_name))        
        with open(module.__file__, 'r') as module_file:
            module = module_utilities.create_module(module_name, module_file.source(), 
                                             attach_source=True)
        sys.modules[module_name] = module
        print "Returning module from disk: ", module, module._source[:128]
        return module
    
        
class String_Importer(object):
    
    sources = {}
    
    @classmethod
    def add_module(cls, module_name, source):
        cls.sources[module_name] = source
    
    @classmethod
    def remove_module(cls, module_name):
        del cls.sources[module_name]
        
    def find_module(self, module_name, path):    
        if module_name in self.sources:
            return self
        return None
        
    def load_module(self, module_name):        
        if module_name in sys.modules:
            return sys.modules[module_name]        
        module = module_utilities.create_module(module_name, self.sources[module_name], 
                                         attach_source=True)
        sys.modules[module_name] = module
        return module    
        
        
class Encrypted_String_Importer(object):

    sources = {}
    key = r''   

    @classmethod
    def add_module(cls, module_name, attribute):
        print "Adding module: ", module_name
        cls.sources[module_name] = attribute
    
    @classmethod
    def remove_module(cls, module_name):
        del cls.sources[module_name]
        
    def find_module(self, module_name, path):    
        if module_name in self.sources:
            print "Module is available as string", module_name
            return self
        print "\tModule not available as string", module_name
        return None
        
    def load_module(self, module_name):
        if module_name in sys.modules:
            print "Returning module from sys.modules", module_name
            return sys.modules[module_name]
        print "------------------Retrieving encrypted module", module_name    
        source = encrypted_source = self.sources[module_name]         
        #source = utilities.convert(encrypted_source, key, ''.join((chr(x) for x in xrange(256))))
        sys.modules[module_name] = module = create_module(module_name, source)        
        print "Returning loaded module", module_name
        return module
               
