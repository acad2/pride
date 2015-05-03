import os
import importlib
import sys
import types
import inspect
import contextlib
import traceback

import mpre.utilities as utilities
import mpre.module_utilities as module_utilities
import mpre.defaults
import mpre.base
create_module = module_utilities.create_module

class Package_Importer(object):
    
    def __init__(self, package):
        self.package = package
            
    def find_module(self, module_path, path=None):
        if module_path in self.package:
            return self
        return None
        
    def load_module(self, module_path):
        try:
            return self.package.get_module(module_path)
        except ImportError:
            print "Could not load module: ", module_path, module_path in self.package.sources
            try:
                return create_module(module_path, self.package.sources[module_path])
            except:
                print "Could not create module: ", module_path
                raise
            
            
class Module(types.ModuleType):
    
    def __new__(cls, module_name, source):
        new_module = super(Module, cls).__new__(cls)        
        module_code = compile(source, module_name, 'exec')
        exec module_code in new_module.__dict__
        new_module._source = source
        return new_module
        
        
class Package(mpre.base.Base):
    
    defaults = mpre.defaults.Package
     
    def _get_subpackages(self):
        return [str(package) for package in self.objects.get("Package", [])]
    subpackages = property(_get_subpackages)
    
    def __init__(self, module, **kwargs):
        self.sources = {}
        super(Package, self).__init__(**kwargs)        
        package_name = self.package_name = module.__name__
        get_source = module_utilities.get_module_source       
        sources = self.sources
        sources[package_name] = get_source(module)
        module_file = module.__file__
        path, init_py = os.path.split(module_file)
        self.path = path
        
        required_modules = self.required_modules = module_utilities.get_required_modules(module)
        self.modules = modules = []
        for _file in os.listdir(path):
            module_name, extension = os.path.splitext(_file)   
            if extension in self.python_extensions:
                modules.append(module_name)
                if module.__package__:
                  #  print "Renaming {} to {}".format(module_name, module.__package__ + "." + module_name)
                    module_name = module.__package__ + '.' + module_name
                    
                required_modules.add(module_name)
                with open(os.path.join(path, _file), 'rb') as py_file:
                    sources[module_name] = py_file.read()
                    
                if not sources[module_name]:
                    continue
                try:
                 #   print "Compiling", module_name
                    _module = module_utilities.create_module(module_name, sources[module_name])
                except:
                    print "Unable to compile module: {}. Unable to determine required modules".format(module_name)                 
                   # print traceback.format_exc()
                else:
                    required_modules.update(module_utilities.get_required_modules(_module))
                
            elif os.path.exists(os.path.join(path, _file, "__init__.py")):
                subpackage = importlib.import_module(_file)
                self.create(Package, subpackage, sources=sources)            
        
        for subpackage in self.objects.get("Package", []):
            self.required_modules.update(subpackage.required_modules)            
        
        for module_name in required_modules:
            print "Ensuring source for {} exists".format(module_name)
            if module_name not in sources and self.include_all_source:
                try:
                    sources[module_name] = (get_source(sys.modules[module_name] if 
                                            module_name in sys.modules else
                                            get_source(importlib.import_module(module_name))))
                except TypeError:
#                    print "Could not get source for module: ", module_name
                    sources[module_name] = None

        if self.include_documentation:
            self.create("mpre.package.Documentation", module)            
    
    def get_module(self, module_name):        
       # package_prefix = self.package_name + '.'
       # string_size = len(package_prefix)
        #if module_name[:string_size] == package_prefix:
         #   if string_size != len(module_name):
          #      module_name = module_name[string_size:]
        try:
            source = self.sources[module_name]
            if not source:
                raise KeyError
        except KeyError:
            raise ImportError("Module '{}' not in package '{}'".format(module_name, 
                                                                       self.package_name))       
        return module_utilities.create_module(module_name, source)

    def __contains__(self, module_name):
        return module_name in self.sources
                                
    def __str__(self):
        return self.instance_name + ": " + self.package_name
        
        
class Documentation(mpre.base.Base):
        
    def __init__(self, _object, **kwargs):
        super(Documentation, self).__init__(**kwargs)        
        self.documentation = utilities.documentation(_object)

      #  documentation = [''.join((getattr(_object, "__name__", type(object).__name__), 
      #                           "\n==========\n", documentation))]
        """documentation = [documentation]
        if isinstance(_object, types.ModuleType):
            for attribute in getattr(_object, "__all__", dir(_object)):
                module_object = getattr(_object, attribute)
                if isinstance(module_object, type) and attribute[0] != "_":
                    docstring = (module_object.__doc__ if module_object.__doc__ else 
                                 'No Documentation available')
                    documentation.append("\n" + ''.join((attribute, "\n--------\n", docstring)))
        
        self.documentation = "\n".join(documentation)"""
        
    def generate_md_file(self, module_name):
        """usage: documentation.generate_md_file(module_name) => documentation"""
        null_docstring = 'No documentation available'
        with ignore_instructions():
            try:
                module = importlib.import_module(module_name)
            except:
                print traceback.format_exc()
                documentation = null_docstring
            else:
                module_docstring = module.__doc__ if module.__doc__ else null_docstring
                    
                documentation = [''.join((module_name, "\n========\n", module_docstring))]
                                    
                for attribute in getattr(module, "__all__", dir(module)):
                    module_object = getattr(module, attribute)
                    if isinstance(module_object, type) and attribute[0] != "_":
                        docstring = module_object.__doc__ if module_object.__doc__ else null_docstring
                        documentation.append("\n" + ''.join((attribute, "\n--------\n", docstring)))
                            
        return "\n".join(documentation)        