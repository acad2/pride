import inspect
import sys
import importlib
import contextlib

@contextlib.contextmanager
def sys_meta_path_switched(new_meta_path):
    backup = sys.meta_path
    sys.meta_path = new_meta_path
    try:
        yield
    finally:
        sys.meta_path = backup
        

class From_Disk(object):
        
    def __init__(self, modules=tuple()):
        self.modules = modules
        
    def find_module(self, module_name, path):
        if not self.modules or module_name in self.modules:
            return self
        return None
        
    def load_module(self, module_name):
        del sys.modules[module_name]
        sys.modules[module_name] = module = importlib.import_module(module_name)
        return module