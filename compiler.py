import os
import sys

from math import sqrt
import multiprocessing as mp

import mpre.base as base
import mpre.defaults as defaults
import mpre.misc._compile as _compile

class Compiler(base.Base):
    
    defaults = defaults.Base.copy()
    defaults.update({"shared_file_type" : "pyd" if "win" in sys.platform else "so",
                     "directory" : os.getcwd(),
                     "subfolders" : tuple(),
                     "main_file" : '',
                     "ignore_files" : tuple(),
                     "max_processes" : 10})
                     
    def __init__(self, **kwargs):
        super(Compiler, self).__init__(**kwargs)               
            
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
        
        processes = []
        for file_count in range(files_per_process):
            processes.append(mp.Process(target=_compile.py_to_compiled, 
                                        args=[files[slices[file_count]],
                                        self.shared_file_type]))
        print "beginning compilation..."
        for process in processes:
            process.start()
                        
        print "waiting for shared resources to finish compiling..."        
        for process in processes:            
            process.join()
            
        if main_file:
            print "compiling executable..."
            executable = _compile.py_to_compiled([main_file], 'exe')
            print "...done"
            
if __name__ == "__main__":
    compiler = Compiler(subfolders=("audio", "gui", "misc", "programs"),
                        main_file='',#"metapython.py",
                        ignore_files=["compiler.py", "_compile.py"])
    compiler.compile()