import sys
import importlib

import pride.base

class Patched_Module(pride.base.Wrapper):
    """ The base class for patching modules """
    
    defaults = {"module_name" : ''}
    
    def __init__(self, **kwargs):
        super(Patched_Module, self).__init__(**kwargs)
        self.wraps(importlib.import_module(self.module_name))
        sys.modules[self.module_name] = self
        
 
class File_Logger(pride.base.Wrapper):
    
    defaults = {"file" : None, "log_type" : "StringIO.StringIO"}
    
    def __init__(self, **kwargs):
        super(File_Logger, self).__init__(**kwargs)
        self.log = self.create("pride.fileio.File", file_type=self.log_type)
        
    def write(self, data):
        self.log.write(data)
        self.file.write(data)
        self.file.flush()
            
        
class Patched_sys(Patched_Module):
            
    defaults = {"module_name" : "sys"}
    
    def _get_stdout(self):
        return self.wrapped_object.stdout
    def _set_stdout(self, value):
        self._logger.wraps(value) 
        self.wrapped_object.stdout = self._logger        
    stdout = property(_get_stdout, _set_stdout)               
    
    def __init__(self, **kwargs):
        super(Patched_sys, self).__init__(**kwargs)
        self._logger = File_Logger(file=sys.stdout)
        sys.stdout_log = self._logger.log        