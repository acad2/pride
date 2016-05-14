import types
import sys
import contextlib
import inspect
import symtable
import pkgutil

import contextmanagers

def installed_modules(directories=None):
    """ Returns a list of the names of available python modules """
    return [module[1] for module in pkgutil.iter_modules(directories)]
            
def create_module(module_name, source, context=None):
    """ Creates a module with the supplied name and source"""
    module_code = compile(source, module_name, 'exec')
    new_module = types.ModuleType(module_name)
    if context:
        new_module.__dict__.update(context)            
    exec module_code in new_module.__dict__
    return new_module
  
def get_module_source(module):
    """ Retrieve the source code of module. If the source code has been
        processed by the pride compiler, the preprocessed code is returned
        from the compilers cache. Otherwise, the inspect module is used. """
    try:
        return pride.compiler.module_source[module.__name__]
    except KeyError:        
        return inspect.getsource(module)
    
def reload_module(module_name):
    """ Reloads the module specified by module_name"""
    reload(sys.modules[module_name])
     
@contextlib.contextmanager
def modules_preserved(modules=tuple()):
    """ Enter a context where the modules specified will be backed up + restored upon exit
        If modules is not specified, all modules in sys.modules are backed up and resotred. """
    backup = {}
    if not modules:
        modules = [key for key in sys.modules if sys.modules[key]]
    for module_name in modules:
        if module_name not in sys.modules:
            raise ValueError("Attempted to preserve non existent module: {}".format(module_name))
        backup[module_name] = sys.modules[module_name]                  
    try:
        yield
    finally:
        for name, module in backup.items():
            if module is not None:
                sys.modules[name] = module
        
@contextlib.contextmanager
def modules_switched(module_dict):
    """ Enters a context where the modules named in module_dict keys are 
        recompiled and replaced by the associated source. The original 
        modules will be restored upon exit. """
    modules = {}
    with modules_preserved(module_dict.keys()):
        for module_name, source_code in module_dict.items():
            try:
                module = sys.modules.pop(module_name)
            except KeyError:
                module = importlib.import_module(module_name)                
            filepath = (module.__file__ if module.__file__[-1] != 'c' else
                        module.__file__[:-1])
            with contextmanagers.file_contents_swapped(source_code, filepath):
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
            try:
                module_source[module_name] = ''.join(pride.compiler.module_source[module_name][0])
            except KeyError:
                module = importlib.import_module(module_name)
                try:
                    module_source[module_name] = inspect.getsource(module)
                except (IOError, TypeError):                    
                    module_source[module_name] = None

    return module_source       
    
def get_all_modules_for_class(_class):            
    class_mro = _class.__mro__[:-1] # don't get objects source
    class_info = [(cls, cls.__module__) for cls in reversed(class_mro)]  # beginning at the root
    required_modules = []
    with modules_preserved(info[1] for info in class_info):
        compiler = sys.meta_path[0]
        for cls, module_name in class_info:
            module = compiler.reload_module(module_name)            
            source = ''.join(compiler.module_source[module_name][0])            
            required_modules.append((module_name, source, module))    
    return required_modules
    