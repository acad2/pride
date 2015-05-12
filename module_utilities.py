import types
import sys
import contextlib
        
def create_module(module_name, source, context=None):
    """ Creates a module with the supplied name and source"""
    module_code = compile(source, module_name, 'exec')
    new_module = types.ModuleType(module_name)
    if context:
        for key, value in context.items():
            setattr(new_module, key, value)    
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
                package = value.__package__
                if name == package:
                    packages.add(name)
                              
                if name not in required_modules:  
                 #   print "Adding {} to required_modules".format(name)                        
                    required_modules.add(name)
                    module_modules, module_packages = _get_modules(value, 
                                                                   required_modules, 
                                                                   packages)
                    required_modules.update(module_modules)
                    packages.update(module_packages)
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