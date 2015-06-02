#!/usr/bin/env python
""" Launcher script for the Metapython runtime environment. This script starts a metapython     
    session, and the first positional argument supplied is interpreted as the filepath of the
    python script to execute. ."""
from __future__ import unicode_literals
import traceback
import mpre._metapython
Shell = mpre._metapython.Shell
        
if __name__ == "__main__":
    metapython = mpre._metapython.Metapython(parse_args=True)
    while True:    
        try:
            metapython.start_machine()
        except BaseException as error:
            if isinstance(error, SystemExit) or isinstance(error, KeyboardInterrupt):
                raise
            else:
                metapython.alert("Critical Failure\n{}", [traceback.format_exc()], level=0)
                # submit error report here
                # options: continue at last Instruction, reload saved point, request fix via network
                response = raw_input("Please select one: continue/reload ").lower()
                if "reload" in response:
                    metapython = metapython.load(metapython.backup_point)
               # elif "request_fix" in response:
                #    raise NotImplementedError
            
    metapython.alert("shutting down", [metapython.instance_name], level='v')
    metapython.exit()