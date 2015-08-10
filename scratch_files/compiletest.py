import inspect
import os
import sys
import ctypes

import mpre.base

if 'win' in sys.platform:
    IS_WINDOWS = True
else:
    IS_WINDOWS = False
    
class Compiled(object):
    
    def __init__(self, function, name=''):
        source = function.__doc__
        name = name or function.__name__
        self.compile(source, name)
        self.dll = loader.LoadLibrary(name)
        self.__call__ = getattr(self.dll, name)
        
    def compile(self, source, name):    
        with open(name + ".c", 'w') as source_file:
            source_file.write(source)
        os.system("gcc {}.c -o {}.{}".format(name, name, SHARED_OBJECT_TYPE))
    
class Interpreter(mpre.base.Base):
     
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"shared_object_type" : 'dll' if IS_WINDOWS else 'so',
                     "loader" : ctypes.windll if IS_WINDOWS else ctypes.cdll})
                     
    def compile_shared_library(self, source, name):    
        with open(name + ".c", 'w') as source_file:
            source_file.write(source)
        mpre.utilities.shell("gcc {}.c -o {}.{}".format(name, name, self.shared_object_type), True)

    def load_shared_library(self, name):
        return self.loader.LoadLibrary(name)
        
        
if __name__ == "__main__":
    def main():
        """/* Hello World program */

#include<stdio.h>

main()
{
    printf("Hello World");


}"""
    compiled_test = Compiled(main)
    compiled_test()