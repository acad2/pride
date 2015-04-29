import os
import sys

from math import sqrt
import multiprocessing as mp

import _compile

class Compiler(object):
    """ Cross compiles .py files to .pyx, then to .c via cython, then to .pyd or .so via gcc.
        Usage of this class requires cython and gcc to be installed. Note that this class
        currently does not yet type any variables in the source code, and the resulting 
        executable may not perform any faster then one interpreted from .py source. However,
        the executable created is more difficult to reverse engineer then one created by py2exe."""
    def __init__(self, shared_file_system="pyd" if "win" in sys.platform else "so",
                       directory=os.getcwd(),
                       subfolders=tuple(),
                       main_file='',
                       ignore_files=tuple(),
                       ignore_folders=tuple(),
                       max_processes=10):
        self.shared_file_system = shared_file_system
        self.directory = directory
        self.subfolders = subfolders
        self.main_file = main_file
        self.ignore_files = ignore_files
        self.ignore_folders = ignore_folders
        self.max_processes = max_processes
                     
    def cleanup_compiled_files(self, file_systems=("pyx", "c")):  
        directory = self.directory
        _, _, file_list = next(os.walk(directory))
        file_list = [('', file_list)]
        
        for subfolder in self.subfolders:
            folder_path = os.path.join(directory, subfolder)
            file_list.append((folder_path,
                              next(os.walk(folder_path))[2]))
         
        for filetype in file_systems:
            for folder, _files in file_list:
                for _file in _files:
                    if os.path.splitext(_file)[-1] == '.' + filetype:
                        os.remove(os.path.join(folder, _file))
                     
    def get_py_files(self, directory):
        _, _, file_list = next(os.walk(directory))
        return [os.path.join(directory, _file) for _file in file_list if 
                ".py" == os.path.splitext(_file)[-1] and _file not in
                self.ignore_files]
                  
    def compile(self):    
        directory = self.directory
        files = []
        files.extend(self.get_py_files(directory))
        
        for subfolder in self.subfolders:
            files.extend(self.get_py_files(os.path.join(directory, subfolder)))
                     
        if self.main_file:
            main_file = os.path.join(directory, self.main_file)
            files.remove(main_file)
        else:
            main_file = '' # just making shared objects, no executable
        
        file_count = len(files)    
        process_count = min(self.max_processes, int(sqrt(file_count)))
        files_per_process = len(files) / process_count 
        
        # maps consecutive ints (0, 1, 2...) to slices like [0:files_per_process]
        slices = dict((index, 
                       slice(index * files_per_process,
                            (index + 1) * files_per_process))
                       for index in range(files_per_process))
        
        
        if max_processes > 1:
            processes = []
            for file_count in range(files_per_process):
                processes.append(mp.Process(target=_compile.py_to_compiled, 
                                            args=[files[slices[file_count]],
                                            self.shared_file_system]))
            print "beginning compilation..."
            for process in processes:
                process.start()
                            
            print "waiting for shared resources to finish compiling..."        
            for process in processes:            
                process.join()
       # else:
        #    for file in files:
                
        if main_file:
            print "compiling executable..."
            executable = _compile.py_to_compiled([main_file], 'exe')
            print "...done"
            
if __name__ == "__main__":
    compiler = Compiler(subfolders=("audio", "gui", "misc", "programs"),
                        main_file="metapython.py",
                        ignore_files=["compiler.py", "_compile.py"])
    compiler.compile()
    compiler.cleanup_compiled_files(file_systems=("pyx", 'c'))