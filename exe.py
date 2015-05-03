import importlib
import os
import sys
import inspect

import mpre.base
import mpre.defaults
import mpre.utilities as utilities
import mpre.module_utilities as module_utilities
import mpre._compile
import mpre.fileio
import mpre.importers

class Loader(mpre.base.Base):
    
    defaults = mpre.defaults.Loader
        
    def __init__(self, **kwargs):
        super(Loader, self).__init__(**kwargs)
        self.source = self.build()
        
    def build(self):
        source = ''
        for module_name in self.required_imports:
            source += "import " + module_name + "\n"
            
        for _object in self.embedded_objects:
            _object = utilities.resolve_string(_object)
            source += inspect.getsource(_object)
            if isinstance(_object, type):
                source += "\n\n"
            else:
                source += "\n"
                
        source += inspect.getsource(utilities.resolve_string(self.importer)) + "\n\n"
        source += "_importer = " + self.importer.split(".")[-1] + "\n"
        source += "sys.meta_path = []"
        return source 
    
    
class Executable(mpre.base.Base):    
    
    defaults = mpre.defaults.Executable
                           
    def __init__(self, module, **kwargs):
        super(Executable, self).__init__(**kwargs)
        self.file = mpre.fileio.File(self.filename, 'w+b')
        self.main_source = inspect.getsource(module) if not self.main_source else self.main_source
        self.loader = self.create(self.loader_type)
        assert self.main_source
        
    def build(self):
        _file = self.file        
        _file.write(self.loader.source + "\n\n")      
        
        embed_package = "{}_package = r'''{}'''\n\n"
        add_to_path = "sys.meta_path.append(_importer(load({}_package)))\n\n"
        for package in self.packages:
            _file.write(embed_package.format(package.package_name, package.save()))
            _file.write(add_to_path.format(package.package_name))
        _file.write("\n\n")
        _file.write(self.main_source)
        _file.flush()
        print "Compiling..."
        mpre._compile.py_to_compiled([self.filename], 'exe')        
        _file.close()
        
if __name__ == "__main__":
    import mpre
    import mpre.metapython
    import mpre.package
    exe = Executable(mpre.metapython, packages=[mpre.package.Package(mpre)])
    exe.build()