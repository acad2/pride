import os
import platform

import mpre.base
import mpre.utilities

os_type = platform.system()

COMPILE_COMMAND = "gcc {} -IC:\Python27\include -LC:\Python27\libs\ -lpython27 -o {}" if "Windows" == os_type else "gcc {} -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o {}"
class Cython(mpre.base.Base):

    def handle_source(self, source, module_name, 
                      mode="pyd"):
        """ Converts .py source to .c """
        pyx_filename = module_name + ".pyx"
        with open(pyx_filename, 'w') as _file:
            _file.write(source)
            _file.flush()
        
        input_string = ("cython {} --embed" if mode is 'exe' else
                        "cython {}").format(pyx_filename)
        mpre.utilities.shell(input_string)
        os.remove(pyx_filename)
        
        c_filename = module_name + ".c"
        out_filename = module_name + '.' + mode
        mpre.utilities.shell(COMPILE_COMMAND.format(c_filename, out_filename))
        
        os.remove(c_filename)
        
if __name__ == "__main__":
    import inspect
    import mpre.base
    source = inspect.getsource(mpre.base)
    cython = Cython()
    cython.handle_source(source, "mpre.base")