""" pride.patch - utilities for patching python standard library modules
    Patches named in pride.patch.patches will automatically be instantiated
    when pride is imported. """
import sys as sys_module
import importlib as _importlib
import contextlib as _contextlib

import pride.base

patches = ("sys", )

class Patched_Module(pride.base.Wrapper):
    """ The base class for patching modules """
    
    defaults = {"module_name" : ''}
    wrapped_object_name = "module"
    
    def __init__(self, **kwargs):
        super(Patched_Module, self).__init__(**kwargs)
        self.wraps(_importlib.import_module(self.module_name))
        sys_module.modules[self.module_name] = self
        globals()[self.module_name] = self
            
 
class Stdout(pride.base.Base):
    
    defaults = {"file" : None, "log_type" : "StringIO.StringIO", 
                "limit_log_size" : 1024 * 1024, "logging_enabled" : True}    
    
    def __init__(self, **kwargs):
        super(Stdout, self).__init__(**kwargs)
        self.log = self.create("pride.fileio.File", file_type=self.log_type)
        
    def write(self, data):
        if self.limit_log_size and self.log.tell() > self.limit_log_size:
            self.log.truncate()
        if self.logging_enabled:            
            self.log.write(data)
            self.log.flush()        
        self.file.write(data)
        self.file.flush()                
        
    def flush(self):
        self.file.flush()
        
    @_contextlib.contextmanager
    def switched(self, _file):
        backup = self.file
        sys_module.stdout = _file        
        try:
            yield self
        finally: 
            sys_module.stdout = backup        
        
        
class sys(Patched_Module):
            
    defaults = {"module_name" : "sys"}
    
    def _get_stdout(self):
        return self._logger#.wrapped_object
    def _set_stdout(self, value):
        if value is None or value is self._logger:
            value = self.wrapped_object.__stdout__
        self._logger.file = value
    stdout = property(_get_stdout, _set_stdout)               
    
    def __init__(self, **kwargs):
        super(sys, self).__init__(**kwargs)
        self._logger = self.create(Stdout, file=self.wrapped_object.__stdout__)
        self.stdout_log = self._logger.log            
        self.wrapped_object.stdout = self._logger
        
        
class inspect(Patched_Module):
            
    defaults = {"module_name" : "inspect"}
    
    def get_source(_object):
        try:
            return pride.compiler.module_source[_object.__name__][0]
        except KeyError:
            return inspect.getsource(_object)
            
            
            
        