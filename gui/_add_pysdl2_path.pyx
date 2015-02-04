import os
from sys import platform

if "win" in platform:
    filepath = "C:\\Program Files (x86)\\Startup\\"
            
    if not os.path.exists(filepath) or not os.path.isdir(filepath):
        os.makedirs(filepath)
    
    filepath += "pysdl2_environ.bat"
    
    file_info = filepath, 'w'
    command = "setx PYSDL2_DLL_PATH 'C:\\Python27\\DLLs'"
    
else:
    filepath = "~/.bashrc"
    file_info = filepath, 'a'
    command = "export PYSDL2_DLL_PATH='C:\\Python27\\DLLs'"
    
def add_pysdl2_to_environ():
    with open(*file_info) as _file:
        _file.write(command)
        _file.flush()
        _file.close()
        
if __name__ == "__main__":
    add_pysdl2_to_environ()        