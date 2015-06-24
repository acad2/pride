import inspect
import os
import sys
import ctypes

if 'win' in sys.platform:
    shared_object_type = 'dll'
    loader = ctypes.windll
else:
    shared_object_type = 'so'
    loader = ctypes.cdll
    
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
        os.system("gcc {}.c -o {}.exe".format(name, name, 'dll' if 'win' in sys.platform else 'so'))
    
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