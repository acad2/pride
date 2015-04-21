#!/usr/bin/env python
""" Launcher script for the Metapython runtime environment. This script starts a metapython     
    session, and the first positional argument supplied is interpreted as the filepath of the
    python script to execute"""
from __future__ import unicode_literals
import mpre._metapython
Shell = mpre._metapython.Shell
        
if __name__ == "__main__":
    metapython = mpre._metapython.Metapython(parse_args=True)
    metapython.start_machine()
    metapython.alert("shutting down", [metapython.instance_name], level='v')
    metapython.exit()