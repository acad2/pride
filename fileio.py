import sys
import importlib
import contextlib
import mpre.utilities as utilities
    
@contextlib.contextmanager
def sys_meta_path_switched(new_meta_path):
    backup = sys.meta_path
    sys.meta_path = new_meta_path
    print "Switched meta path: ", sys.meta_path
    try:
        yield
    finally:
        sys.meta_path = backup
        
class From_Disk_Importer(object):
        
    def find_module(self, module_name, path):
        print "Finding module", module_name
        return self
        
    def load_module(self, module_name):
        print "Loading module from disk", module_name
        module = (sys.modules[module_name] if module_name in sys.modules else
                  importlib.import_module(module_name))        
        with open(module.__file__, 'r') as module_file:
            module = utilities.create_module(module_name, module_file.source(), 
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
        module = utilities.create_module(module_name, self.sources[module_name], 
                                         attach_source=True)
        sys.modules[module_name] = module
        return module    
        
        
class Encrypted_String_Importer(String_Importer):

    sources = {}
                   
    def load_module(self, module_name):
        if module_name in sys.modules:
            return sys.modules[module_name]
        main = sys.modules["__main__"]
        print "------------------Retrieving module from virtual encrypted file", module_name
        saved_file_stream = self.sources[module_name]        
        saved_file = load(saved_file_stream)        
        sys.modules[module_name] = module = create_module(module_name, saved_file.read())
        
        print "Returning loaded module", module_name
        return module
               
