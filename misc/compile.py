if __name__ == "__main__":
    import os
    import sys
    from math import sqrt
    import multiprocessing as mp
    from _compile import py_to_compiled
    MAX_PROCESSES = 10
        
    # convert .py files in this directory to .pyd or .so (windows/linux)
    shared_filetype = "pyd" if "win" in sys.platform else "so"
    directory = os.getcwd()
    _, _, file_list = next(os.walk(directory))
    file_list = [_file for _file in file_list if "py" == _file.split(".")[-1]]
    try:
        main_file = sys.argv[1]
    except IndexError:
        main_file = None
    else:
        file_list.remove(main_file)
    
   # file_list = ["pagebuilder.py"]
    print main_file, file_list
    
    file_count = len(file_list)    
    process_count = min(MAX_PROCESSES, int(sqrt(file_count)))
    files_per_process = len(file_list) / process_count 
    
    # maps consecutive ints (0, 1, 2...) to slices like [0:files_per_process]
    slices = dict((index, slice(index * files_per_process, (index + 1) *files_per_process)) for index in range(files_per_process))
    
    processes = []
    for file_count in range(files_per_process):
        processes.append(mp.Process(target=py_to_compiled, 
                                    args=[file_list[slices[file_count]],
                                       shared_filetype]
                                 ))
    print "beginning compilation..."
    for process in processes:
        process.start()
        
    print "waiting for shared resources to finish compiling..."        
    for process in processes:
        
        process.join()
        
    if main_file:
        print "compiling executable..."
        executable = py_to_compiled([main_file], 'exe')
        print "...done"