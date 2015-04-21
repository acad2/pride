mpre.compiler
========
No documentation available

Compiler
--------
 Cross compiles .py files to .pyx, then to .c via cython, then to .pyd or .so via gcc.
        Usage of this class requires cython and gcc to be installed. Note that this class
        currently does not yet type any variables in the source code, and the resulting 
        executable may not perform any faster then one interpreted from .py source. However,
        the executable created is more difficult to reverse engineer then one created by py2exe.