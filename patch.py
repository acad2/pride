import sys
import importlib
import contextlib

import pride.base

patches = ("Sys", )

class Patched_Module(pride.base.Wrapper):
    """ The base class for patching modules """
    
    defaults = {"module_name" : ''}
    
    def __init__(self, **kwargs):
        super(Patched_Module, self).__init__(**kwargs)
        self.wraps(importlib.import_module(self.module_name))
        sys.modules[self.module_name] = self
        globals()[self.module_name] = self
            
 
class Stdout(pride.base.Wrapper):
    
    defaults = {"file" : None, "log_type" : "StringIO.StringIO"}
    wrapped_object_name = "file"
    
    def __init__(self, **kwargs):
        super(Stdout, self).__init__(**kwargs)
        self.log = self.create("pride.fileio.File", file_type=self.log_type)
        
    def write(self, data):
        self.log.write(data)
        self.file.write(data)
        self.file.flush()
     
    @contextlib.contextmanager
    def switched(self, _file):
        backup = self.file
        sys.stdout = _file
        try:
            yield self
        finally:            
            sys.stdout = backup        
        
        
class Sys(Patched_Module):
            
    defaults = {"module_name" : "sys"}
    
    def _get_stdout(self):
        return self._logger#.wrapped_object
    def _set_stdout(self, value):
        if value is None or value is self._logger:
            value = self.wrapped_object.__stdout__
        self._logger.wraps(value)         
    stdout = property(_get_stdout, _set_stdout)               
    
    def __init__(self, **kwargs):
        super(Sys, self).__init__(**kwargs)
        self._logger = self.create(Stdout, file=sys.stdout)
        Sys.stdout_log = self._logger.log        
        self.stdout = self.wrapped_object.stdout
        