from sys import platform
import subprocess

COMPILE_COMMAND = "gcc {} -IC:\Python27\include -LC:\Python27\libs\ -lpython27 -o {}." if "win" in platform else "gcc {} -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o {}. "

def convert_to_pyx(file_list):
    new_names = []

    for filename in file_list:
        #filepath = directory + "\\" + filename
        #new_path = filepath + 'x'
        filepath = filename
        new_path = filename + 'x'
        
        old_file = open(filepath, 'rb')
        new_file = open(new_path, 'wb')
        new_file.write(old_file.read())
        new_file.flush()
        new_file.close()
        old_file.close()
        
        new_name = new_path.split("\\")[-1]
        new_names.append(new_name)
        #print "{} converted to {}".format(filename, new_name)
    #print
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
            #print "{} cross compiled successfully to {}{}".format(filename, new_name, output.read())
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