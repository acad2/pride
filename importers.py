""" Contains import related functions and objects, including the compiler """
import inspect
import sys
import importlib
import contextlib
import types
import imp
import tokenize
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
    
@contextlib.contextmanager
def sys_meta_path_switched(new_meta_path):
    backup = sys.meta_path
    sys.meta_path = new_meta_path
    try:
        yield
    finally:
        sys.meta_path = backup

@contextlib.contextmanager        
def imports_from_disk():
    with sys_meta_path_switched([From_Disk()]):
        yield
                    
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
        
class Compiler(object):
    """ Compiles python source to bytecode. Source may be preprocessed.
        This object is automatically instantiated and inserted into
        sys.meta_path as the first entry. """
    def __init__(self, preprocessors=tuple()):
        self.preprocessors = preprocessors
        self.module_source = {}
        
    def find_module(self, module_name, path):
        modules = module_name.split('.')
        loader = None
        end_of_modules = len(modules) - 1
        for count, module in enumerate(modules):
            try:
                _file, path, description = imp.find_module(module, path)
            except ImportError:
                pass
            else:
                if path.split('.')[-1] == "pyd":
                    continue
                if _file:
                    self.module_source[module_name] = (_file.read(), path)
                    if count == end_of_modules:
                        loader = self
        return loader        
  
    def load_module(self, module_name):
        if module_name not in sys.modules:
            source, path = self.module_source[module_name]
            sys.modules[module_name] = self.compile_module(module_name,
                                                           source,
                                                           path)
        return sys.modules[module_name]
                    
    def compile_module(self, module_name, source, path):
        new_module = types.ModuleType(module_name) 
        module_code = self.compile_source(source, module_name)
        new_module.__file__ = path
        exec module_code in new_module.__dict__           
        return new_module
    
    def preprocess(self, source):
        for preprocessor in self.preprocessors:
            source = preprocessor.handle_input(source)
        return source
        
    def compile_source(self, source, filename=''):
        return compile(self.preprocess(source), filename, 'exec')         
        
        
class Dollar_Sign_Directive(object):
    """ Replaces '$' directive with mpre.objects lookup. This
        facilitates the syntatic sugar $Component, which is
        translated to mpre.objects['Component']. """
        
    def handle_input(self, source):
        readline = StringIO.StringIO(source).readline
        found = False
        new_source = []
        for _type, token, _, _, _ in tokenize.generate_tokens(readline):   
            if found:
                token = "mpre.objects['{}']".format(token)
                found = False
            if token == '$':
                found = True
            else:
                new_source.append((_type, token))       
        return #tokenize.untokenize(new_source)        