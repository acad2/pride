#!/usr/bin/env python
""" Launcher script for the Python Runtime and Integrated Development Environment. 
    This script starts a python session, and the first positional argument supplied is
    interpreted as the filepath of the python script to execute. ."""
from __future__ import unicode_literals
from platform import python_version_tuple
if python_version_tuple()[0] == '3':
    from past.builtins import xrange
    
def main(): 
    import pride.interpreter
    running = True
    while running:
        assert "/Python" not in pride.objects
        python = pride.interpreter.Python(parse_args=True)                
        try:            
            python.start_machine()                
        except BaseException as error:                        
            running = False                        
            pride.objects["/Finalizer"].run()                        
            if isinstance(error, SystemExit) or isinstance(error, KeyboardInterrupt):
                python.alert("Session shutdown intiated... ", level=python.verbosity["shutdown"])                   
                if getattr(error, "code", '') == "Restart":
                    try:
                        pride.objects["/User"].delete()
                    except KeyError:
                        if "/User" in pride.objects:
                            raise
                    python.alert("Initiating restart.. ", level=python.verbosity["restart"])        
                    python.delete()
                    del python
                    running = True
                else:
                    raise
            else:
                python.alert("Unhandled exception caused a fatal error", level=0)
                raise   

if __name__ == "__main__":
    main()
