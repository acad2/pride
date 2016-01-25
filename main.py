#!/usr/bin/env python
""" Launcher script for the Python Runtime and Integrated Development Environment. 
    This script starts a python session, and the first positional argument supplied is
    interpreted as the filepath of the python script to execute. ."""
from __future__ import unicode_literals
import pride.interpreter

if __name__ == "__main__":
    running = True
    while running:
        python = pride.interpreter.Python(parse_args=True)                
        try:            
            python.start_machine()                
        except BaseException as error:                        
            running = False            
            pride.objects["->Finalizer"].run()            
            if isinstance(error, SystemExit):
                python.alert("System shutdown intiated. Running finalizer... ", 
                            level=python.verbosity["shutdown"])                
                if error.code == "Restart":
                    try:
                        pride.objects["->User"].delete()
                    except KeyError:
                        if "->User" in pride.objects:
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
