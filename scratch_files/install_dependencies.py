import mpre.utilities as utilities

def install_python_dev():
    """ usage: install_python_dev()
        
        Installs python-dev on this machine. Root access is required.
        This fixes the "Python.h: No such file or directory" error"""
    utilities.shell("sudo apt-get install python-dev")
    
if __name__ == "__main__":
    pass