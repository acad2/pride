#!/usr/bin/env python
""" Launcher script for the Python runtime environment. This script starts
    a metapython session, and the first positional argument supplied is
    interpreted as the filepath of the python script to execute. ."""
from __future__ import unicode_literals
import traceback
import mpre.interpreter
Shell = mpre.interpreter.Shell

if __name__ == "__main__":
    metapython = mpre.interpreter.Python(parse_args=True)
    metapython.start_machine()
    #while True:
    #    try:
    #        metapython.start_machine()
    #    except BaseException as error:
    #        raise
    #        if isinstance(error, SystemExit) or isinstance(error, KeyboardInterrupt):
    #            raise
    #        else:
    #            metapython.alert("Critical Failure\n{}", [traceback.format_exc()], level=0)
    #            # submit error report here
    #            # options: continue at last Instruction, reload saved point, 
                 # or maybe request a fix via network
    #            response = raw_input("Please select one: continue/reload ").lower()
    #            if "reload" in response:
    #                metapython = metapython.load(metapython.backup_point)
    #           # elif "request_fix" in response:
    #            #    raise NotImplementedError
            
    metapython.alert("shutting down", [metapython.instance_name], level='v')
    metapython.exit()
    