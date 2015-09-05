import importlib

import mpre.base

class Module_Wrapper(mpre.base.Wrapper):
    
    defaults = mpre.base.Wrapper.defaults.copy()
    defaults.update({"module_name" : ''})
    
    def __init__(self, **kwargs):
        super(Module_Wrapper, self).__init__(**kwargs)
        self.wraps(importlib.import_module(self.module_name))
        
 
class File_Logger(mpre.base.Wrapper):
    
    defaults = mpre.base.Wrapper.defaults.copy()
    defaults.update({"file" : None,
                     "log_type" : "StringIO.StringIO"})
    
    def __init__(self, **kwargs):
        super(File_Logger, self).__init__(**kwargs)
        self.wraps(self.file)
        self.log = self.create(self.log_type)
        
    def write(self, data):
        self.log.write(data)
        self.file.write(data)
        
        
class sys_Wrapper(Module_Wrapper):
            
    defaults = Module_Wrapper.defaults.copy()
    
    def _get_stdout(self):
        return self.wrapped_object.stdout
    def _set_stdout(self, value):
        try:
            mpre.objects[self._last_log].delete()
        except AttributeError:
            pass
        file_logger = self.wrapped_object.stdout = File_Logger(file=value)
        self._last_log = file_logger.instance_name
    stdout = property(_get_stdout, _set_stdout)               
    