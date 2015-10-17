import os
import platform

import pride.base
import pride.utilities

os_type = platform.system()

COMPILE_COMMAND = "gcc {} -IC:\Python27\include -LC:\Python27\libs\ -lpython27 -o {}" if "Windows" == os_type else "gcc {} -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o {}"
class Cython(pride.base.Base):

    def handle_source(self, source, module_name, 
                      mode="pyd"):
        """ Converts .py source to .c """
        pyx_filename = module_name + ".pyx"
        with open(pyx_filename, 'w') as _file:
            _file.write(source)
            _file.flush()
        
        input_string = ("cython {} --embed" if mode is 'exe' else
                        "cython {}").format(pyx_filename)
        pride.utilities.shell(input_string)
        os.remove(pyx_filename)
        
        c_filename = module_name + ".c"
        out_filename = module_name + '.' + mode
        pride.utilities.shell(COMPILE_COMMAND.format(c_filename, out_filename))
        
        os.remove(c_filename)
        
if __name__ == "__main__":
    import inspect
    import pride.base
    source = inspect.getsource(pride.base)
    cython = Cython()
    cython.handle_source(source, "pride.base")