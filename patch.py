import sys
import importlib

import pride.base

class Module_Wrapper(pride.base.Wrapper):
    
    defaults = {"module_name" : ''}
    
    def __init__(self, **kwargs):
        super(Module_Wrapper, self).__init__(**kwargs)
        self.wraps(importlib.import_module(self.module_name))
        sys.modules[self.module_name] = self
        
 
class File_Logger(pride.base.Wrapper):
    
    defaults = {"file" : None,
                "log_type" : "StringIO.StringIO"}
    
    def __init__(self, **kwargs):
        super(File_Logger, self).__init__(**kwargs)
        self.log = self.create(self.log_type)
        
    def write(self, data):
        self.log.write(data)
        self.file.write(data)
        self.file.flush()
        
        
class sys_Wrapper(Module_Wrapper):
            
    defaults = {"module_name" : "sys"}
    
    def _get_stdout(self):
        return self.wrapped_object.stdout
    def _set_stdout(self, value):
        self._logger.wraps(value) 
        self.wrapped_object.stdout = self._logger        
    stdout = property(_get_stdout, _set_stdout)               
    
    def __init__(self, **kwargs):
        super(sys_Wrapper, self).__init__(**kwargs)
        self._logger = File_Logger(file=sys.stdout)
        sys.stdout = self._logger