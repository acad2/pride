import os
from sys import platform
import subprocess
            
COMPILE_COMMAND = "gcc {} -IC:\Python27\include -LC:\Python27\libs\ -lpython27 -o {}." if "win" in platform else "gcc {} -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o {}. "
#gcc primetest.c -IC:\Python27\include -LC:\Python27\libs\ -lpython27 -o primetest.pyd
def convert_to_pyx(file_list):
    new_names = []
    
    for filename in file_list:
        pyx_filename = filename + 'x'
        with open(filename, 'r') as py_file, open(pyx_filename, 'w') as pyx_file:
            pyx_file.truncate(0)
            pyx_file.write(py_file.read())
            pyx_file.flush()
            new_names.append(pyx_filename)
    return new_names

    
def convert_to_c(file_names, mode):
    options = {"stdout" : subprocess.PIPE,
               "stderr" : subprocess.PIPE}
    cross_compile = "cython {} --embed" if mode is 'exe' else "cython {}"
    c_files = []
    
    for filename in file_names:
        command = cross_compile.format(filename)
        compiler = subprocess.Popen(command, **options)
        output, errors = compiler.stdout, compiler.stderr
        
        problem = errors.read()
        if problem:
            print problem
            #raw_input("Continue compiling other modules?")
        else:
            _filename = filename.split(".")[:-1][0]
            new_name = _filename + '.c'
            c_files.append(new_name)
            print "{} cross compiled successfully to {}{}".format(filename, new_name, output.read())
    #print
    return c_files

    
def ccompile(file_list, mode="pyd"):
    compile_mode = mode + " -shared" if mode in ('pyd', 'so') else mode
    
    compile_command = COMPILE_COMMAND + compile_mode
    
    options = {"stdout" : subprocess.PIPE,
               "stderr" : subprocess.PIPE}
               
    compiled = []
    for filename in file_list:
        _filename = ''.join(filename.split(".")[:-1])
        compiler = subprocess.Popen(compile_command.format(filename, _filename), **options)
        output, errors = compiler.stdout, compiler.stderr
        problem = errors.read()
        if problem:
            print problem
        else:
            object_name = _filename + '.' + mode
            print "{} was compiled successfully{}".format(object_name, output.read())
            compiled.append(object_name)
        
    return compiled
    
def py_to_compiled(file_list, mode="pyd"):
    pyx_files = convert_to_pyx(file_list)
    return pyx_to_compiled(pyx_files, mode)
    
def pyx_to_compiled(file_list, mode):
    c_files = convert_to_c(file_list, mode)
    return ccompile(c_files, mode)