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
import mpre.fileio
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
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"python_extensions" : (".py", ".pyx", ".pyd", ".pso", ".so"),
                     "package_name" : None,
                     "include_source" : True,
                     "replace_reference_on_load" : False,
                     "include_documentation" : False,
                     "top_level_package" : ''}) 
     
    def _get_subpackages(self):
        return [package for package in self.objects.get("Package", [])]
    subpackages = property(_get_subpackages)
    
    def __init__(self, module, **kwargs):
        self.sources = {}
        documentation = self.documentation = {}
        super(Package, self).__init__(**kwargs)       
        
        package_name = self.package_name = module.__name__
        top_level_package = self.top_level_package = self.top_level_package or package_name
        include_documentation = self.include_documentation
    
        main_file = getattr(sys.modules["__main__"], "__file__", '__main__')
        module_file = module.__file__
        path, init_py = os.path.split(module_file)
        self.path = path
        
        get_source = module_utilities.get_module_source       
        sources = self.sources
        sources[package_name] = get_source(module)        
        
        required_modules = self.required_modules = module_utilities.get_required_modules(module)
        self.modules = modules = []
        _subpackages = []
        for _file in os.listdir(path):
            module_name, extension = os.path.splitext(_file)   
            if module_name == "__init__":
                continue
            if extension in self.python_extensions:
                modules.append(module_name)
              #  is_main = module_name == main_file
                if module.__package__:
               #     print "Renaming {} to {}".format(module_name, module.__package__ + "." + module_name)
                    module_name = module.__package__ + '.' + module_name

                required_modules.add(module_name)
                with open(os.path.join(path, _file), 'rb') as py_file:
                    source = py_file.read()
                    if self.include_source:
                        sources[module_name] = source
             #   if not source:
              #      print "Could not obtain source for: ", module_name
               #     continue
               # if is_main:
                #    required_modules.update(module_utilities.get_required_modules(module))
                 #   continue                
                try:
                #    print "Compiling", module_name, package_name, _file
                    _module = (sys.modules.get(module_name) or 
                               module_utilities.create_module(module_name, source,
                                                              context={"__file__" : _file,
                                                                       "_source" : source,
                                                                       "__package__" : package_name}))
                except BaseException as error:
                    if type(error) in (KeyboardInterrupt, SystemExit, RuntimeError):
                        raise
                    print "Unable to compile module: {}. Unable to determine required modules".format(module_name)                 
                    print traceback.format_exc()
                else:
                    required_modules.update(module_utilities.get_required_modules(_module))
                    if include_documentation:
                        documentation[module_name] = self.create("mpre.package.Documentation", 
                                                                 _module, path=path,
                                                                 top_level_package=top_level_package) 
                        
            elif os.path.exists(os.path.join(path, _file, "__init__.py")):
                # do subpackages later so modules in appear grouped by package in mkdocs.yml
                _module = importlib.import_module(_file)
                _module.__dict__.setdefault("__package__", _file)
            #    print "Created subpackage: ", _file
                _subpackages.append(_module)                
                
        for subpackage in _subpackages:
            self.create(Package, subpackage, sources=sources, 
                        include_documentation=include_documentation,
                        include_source=self.include_source,
                        top_level_package=top_level_package)            
        
        for subpackage in self.objects.get("Package", []):
            self.required_modules.update(subpackage.required_modules)            
        
        for module_name in required_modules:
            if module_name == "__main__":
          #      print "Ignoring main module", sys.modules["__main__"].__file__
                continue
         #   print "Ensuring source for {} exists".format(module_name)
            if module_name not in sources and self.include_source:
                try:
                    sources[module_name] = (get_source(sys.modules[module_name] if 
                                            module_name in sys.modules else
                                            get_source(importlib.import_module(module_name))))
                except:
           #         print "Could not get source for module: ", module_name
                    sources[module_name] = None
    
        if top_level_package == package_name and self.include_documentation :
            self.documentation[package_name] = self.create("mpre.package.Documentation", module)
            
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
        markdown = self.markdown = utilities.documentation(_object)
        module_name = (_object.__module__ if hasattr(_object, "__module__") else
                       _object.__name__).split(".")[-1]
        module = (_object if isinstance(_object, types.ModuleType) else 
                  sys.modules[module_name])
        path, _file = os.path.split(module.__file__)
   
        self.package_name = package_name = (module.__package__ if 
                                            module.__package__ is not None else
                                            module.__name__.split('.')[0])
        md_filepath = os.path.join(path, "docs", package_name, module_name) + ".md"  
        yml_entry = r"- ['{}', '{}', '{}']" + "\n"

        entry = yml_entry.format(os.path.join(package_name, module_name) + ".md", 
                                 package_name, module_name)
                                     
        yml_file = os.path.join(path, "mkdocs.yml")
        self.write_markdown_file(markdown, md_filepath)
        self.write_yml_entry(entry, yml_file)
        
    def write_yml_entry(self, entry, yml_file):        
        with open(yml_file, 'a+') as _file:
            contents = _file.read()
            # some sort of windows hijinks can cause IOError errno 0 on files opened for appending
            # this makes it happy and stops it from complaining
            _file.seek(_file.tell()) 
            if entry not in contents:
                if not contents:
                    _file.write("site_name: {}\npages:\n".format(self.top_level_package))
                    _file.write("- ['index.md', 'Homepage']\n")
                _file.write(entry)
                _file.flush()                                                            
        
    def write_markdown_file(self, markdown_text, filename):
        with mpre.fileio.File("disk" + os.path.sep + filename, 'w') as md_file: 
            md_file.write(markdown_text)
            md_file.flush()
            