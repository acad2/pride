import importlib
import os
import sys
import inspect
import binascii

import mpre.base

import mpre.utilities as utilities
import mpre.module_utilities as module_utilities
import mpre._compile
import mpre.fileio
import mpre.importers

class Loader(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"required_imports" : ("sys", "hashlib", "pickle", "importlib",
                                           "types", "hmac", "binascii"),
                     "variables"        : {"ASCIIKEY" : "mpre.persistence.ASCIIKEY"},
                     "definitions"      : ("mpre.persistence.authenticated_load", 
                                           "mpre.persistence.load",
                                           "mpre.base.load", 
                                           "mpre.errors.CorruptPickleError",
                                           "mpre.module_utilities.create_module"),
                     "importer"         : ''})
        
    def __init__(self, **kwargs):
        super(Loader, self).__init__(**kwargs)
        self.source = self.build()
        
    def build(self):
        source = '' 
        for module_name in self.required_imports:
            source += "import " + module_name + "\n"
        
        for attribute, value in self.variables.items():
            source += attribute + " = " + repr(utilities.resolve_string(value)) + "\n"
            
        for attribute_path in self.definitions:
            _object = utilities.resolve_string(attribute_path)
            source += inspect.getsource(_object)
            if isinstance(_object, type):
                source += "\n\n"
            else:
                source += "\n"
                
        if self.importer:
            source += inspect.getsource(utilities.resolve_string(self.importer)) + "\n\n"
            source += "_importer = " + self.importer.split(".")[-1] + "\n"
            source += "sys.meta_path = [_importer]"
        return source 
    
    
class Executable(mpre.base.Base):    
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"filename" : "metapython.exe",
                     "package" : None,
                     "file" : None,
                     "loader_type" : "mpre.exe.Loader",
                     "main_source" : '',
                     "use_unicode_literals" : True})   
                           
    def __init__(self, module, **kwargs):
        super(Executable, self).__init__(**kwargs)
        self.file = mpre.fileio.File(self.filename, 'w+b')
        source = inspect.getsource(module) if not self.main_source else self.main_source
        self.main_source = source.replace("from __future__ import unicode_literals", "#from __future__ import unicode_literals")
        self.loader = self.create(self.loader_type)
                
    def build(self):
        _file = self.file        
        if self.use_unicode_literals:
            _file.write("from __future__ import unicode_literals\n")
        
        _file.write(self.loader.source + "\n")      
        
        embed_package = "{}_package = bytes('''{}''')\n\n"
        add_to_path = "sys.meta_path.append(load({}_package))\n\n"
            
        for package in self.packages:
            _file.write(embed_package.format(package.package_name, 
                                             package.save()))
            _file.write(add_to_path.format(package.package_name))
        
        _file.write(self.main_source)
        _file.flush()
        print "Compiling..."
        mpre._compile.py_to_compiled([self.filename], 'exe')        
        _file.close()
        
if __name__ == "__main__":
    import mpre
    import mpre.metapython
    import mpre.package   
    #import mpre.fileio
    packages=[mpre.package.Package(mpre, include_source=True)]       
    exe = Executable(mpre.metapython, packages=[mpre.base.Base(package_name="Test")])#packages)
    exe.build()
    print "Complete"
    #exe.alert("Complete", level=0)