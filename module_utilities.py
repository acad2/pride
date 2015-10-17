import types
import sys
import contextlib
import inspect
import symtable
import pkgutil

def installed_modules(directories=None):
    return [module[1] for module in pkgutil.iter_modules(directories)]
    
#def unused_imports(module):
#    source = inspect.getsource(module)
#    symbol_table = symtable.symtable(source, "string", "exec")
#    return [symbol.get_name() for symbol in symbol_table.get_symbols() if 
#            symbol.is_imported() and not symbol.is_referenced()]
            
def create_module(module_name, source, context=None):
    """ Creates a module with the supplied name and source"""
    module_code = compile(source, module_name, 'exec')
    new_module = types.ModuleType(module_name)
    if context:
        new_module.__dict__.update(context) 
    exec module_code in new_module.__dict__
    return new_module
  
def get_module_source(module):
    try:
        path = module.__file__[:-1] if module.__file__[-1] == 'c' else module.__file__
    except AttributeError:
        raise TypeError("{}.__file__ not found".format(module))
    with open(path, 'rb') as module_file:
        source = module_file.read()
    return source
    
def reload_module(module_name):
    """ Reloads the module specified by module_name"""
    reload(sys.modules[module_name])
     
@contextlib.contextmanager
def modules_preserved(modules=tuple()):
    """ Enter a context where the modules specified will be backed up + restored upon exit"""
    backup = {}
    if not modules:
        modules = [key for key in sys.modules if sys.modules[key]]
    for module_name in modules:
        backup[module_name] = sys.modules.get(module_name, None)
        if backup[module_name] is None:
            print "Attempted to preserve non existent module: ", module_name
    try:
        yield
    finally:
        for name, module in backup.items():
            if module is not None:
                sys.modules[name] = module
        
@contextlib.contextmanager
def modules_switched(module_dict):
    """ Enters a context where the modules in module_dict.keys are replaced by the source
        specified in module_dict[key]. The original modules will be restored upon exit."""
    modules = {}
    with modules_preserved(module_dict.keys()):
        for module_name, source_code in module_dict.items():
            try:
                module = sys.modules.pop(module_name)
            except KeyError:
                module = importlib.import_module(module_name)                
            filepath = (module.__file__ if module.__file__[-1] != 'c' else
                        module.__file__[:-1])
            with file_contents_swapped(source_code, filepath):
                modules[module_name] = importlib.import_module(module_name)
        try:
            yield
        except:
            raise
            pass    

def get_required_modules(module):    
    def _get_modules(module, required_modules, packages):
        for attribute, value in module.__dict__.items():
            if isinstance(value, types.ModuleType):                
                name = value.__name__
                try:
                    package = value.__package__
                except AttributeError:
                    print "module '{}' has no package attribute".format(name)
                    continue
                    
                if name == package:
                    packages.add(name)
                              
                if name not in required_modules:  
                 #   print "Adding {} to required_modules".format(name)                        
                    required_modules.add(name)
                    _modules, _packages = _get_modules(value,   
                                                       required_modules,
                                                       packages)
                    required_modules.update(_modules)
                    packages.update(_packages)
        return required_modules, packages
        
    return _get_modules(module, set(), set())
    
def get_required_sources(modules):
    module_source = {}
    with modules_preserved(modules):
        for module_name in modules:
            module = importlib.import_module(module_name)
            try:
                module_source[module_name] = inspect.getsource(module)
            except (IOError, TypeError):
                module_source[module_name] = None

    return module_source
    
class Module_Listing(object):

    def __init__(self, _file):
        super(Module_Listing, self).__init__()
        self.file = _file        

    def from_help(self):
        helper = pydoc.Helper(output=self.file)
        helper("modules")

    def read_file(self):
        file = self.file
        file.seek(0)
        text = file.read()
        return text

    def trim(self, text):
        _file = StringIO(text)
        found = []
        count = 0
        for line in _file.readlines():
            if line.split(" ").count("") > 2:
                found += line.split()

        return ' '.join(found)

    def get_modules(self):
        self.from_help()
        original = self.read_file()
        return self.trim(original)

    def make_file(self, filename):
        with open(filename, 'w') as _file:
            _file.write(self.get_modules())
            _file.flush()        