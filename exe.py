""" Provides simple utilities for creating cython + gcc compiled 
    executables from python modules. """
import importlib
import os
import sys
import inspect
import binascii

import pride.base

import pride.utilities as utilities
import pride.module_utilities as module_utilities
import pride._compile
import pride.fileio
import pride.importers

class Loader(pride.base.Base):
    """ Used to customize the define bootstrap process. """
    defaults = {"required_imports" : ("sys", "hashlib", "pickle",
                                      "importlib", "types", "hmac",
                                      "binascii"),
                "variables" : {"ASCIIKEY" : "pride.persistence.ASCIIKEY"},
                "definitions" : ("pride.persistence.authenticated_load", 
                                 "pride.persistence.load",
                                 "pride.base.load", 
                                 "pride.errors.CorruptPickleError",
                                 "pride.module_utilities.create_module"),
                "importer" : ''}
        
    def __init__(self, **kwargs):
        super(Loader, self).__init__(**kwargs)
        self.source = self.build()
        
    def build(self):
        source = '' 
        for module_name in self.required_imports:
            source += "import " + module_name + "\n"
        
        for attribute, value in self.variables.items():
            source += attribute + " = " + repr(resolve_string(value)) + "\n"
            
        for attribute_path in self.definitions:
            _object = resolve_string(attribute_path)
            source += inspect.getsource(_object)
            if isinstance(_object, type):
                source += "\n\n"
            else:
                source += "\n"
                
        if self.importer:
            source += inspect.getsource(resolve_string(self.importer)) + "\n\n"
            source += "_importer = " + self.importer.split(".")[-1] + "\n"
            source += "sys.meta_path = [_importer]"
        return source 
    
    
class Executable(pride.base.Base):    
    """ Used to make a cython gcc compiled executable from a python module. """
    defaults = {"filename" : "metapython.exe",
                "package" : None,
                "file" : None,
                "loader_type" : "pride.exe.Loader",
                "main_source" : '',
                "use_unicode_literals" : True}
                           
    def __init__(self, module, **kwargs):
        super(Executable, self).__init__(**kwargs)
        self.file = pride.fileio.File(self.filename, 'w+b')
        source = inspect.getsource(module) if not self.main_source else self.main_source
        self.main_source = source.replace("from __future__ import unicode_literals", "#from __future__ import unicode_literals")
        self.loader = self.create(self.loader_type)
                
    def build(self):
        """ Builds the executable source in python and compiles it
            via cython and gcc. """
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
        pride._compile.py_to_compiled([self.filename], 'exe')        
        _file.close()
        
if __name__ == "__main__":
    import pride
    import pride.main
    import pride.package   
    #import pride.fileio
    packages=[pride.package.Package(pride, include_source=True)]       
    exe = Executable(pride.main, packages=[pride.base.Base(package_name="Test")])#packages)
    exe.build()
    print "Complete"
    #exe.alert("Complete", level=0)