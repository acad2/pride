import types
import sys
import os
import importlib

class Compiler(object):
    
    def __init__(self, packages=("pride", "pride.audio"), preprocessors=tuple()):
        self.packages = packages
        self.preprocessors = preprocessors
        self.module_source = {}
        
    def find_module(self, module_name, path):
        modules = module_name.split('.')
        print module_name, path
        if modules[0] in self.packages:
            filepath = os.path.join(path[0],
                                    os.path.sep.join(modules[1:])) + ".py"
            if os.path.exists(filepath):
                with open(filepath, 'r') as module_file:
                    source = module_file.read() 
                self.module_source[module_name] = source
                return self            
                
    def load_module(self, module_name):
        source = self.module_source[module_name]
        module = sys.modules[module_name] = self.compile_module(module_name, 
                                                                source)
        return module
            
    def compile_module(self, module_name, source):        
        new_module = types.ModuleType(module_name) 
        module_code = self.compile(source, module_name)
        exec module_code in new_module.__dict__        
        return new_module
    
    def preprocess(self, source):
        for preprocessor in self.preprocessors:
            source = preprocessor.handle_input(source)
        return source
        
    def compile(self, source, filename=''):
        return compile(self.preprocess(source), filename, 'exec')       
          
compiler = Compiler()
sys.meta_path.insert(0, compiler)

import pride.base
print pride.base