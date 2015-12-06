#!/usr/bin/env python
""" Launcher script for the Python runtime environment. This script starts
    a python session, and the first positional argument supplied is
    interpreted as the filepath of the python script to execute. ."""
from __future__ import unicode_literals
import pride.interpreter
import pride.usertest

if __name__ == "__main__":
    user = pride.usertest.User(parse_args=True)
    PYTHON = pride.interpreter.Python(parse_args=True)
    PYTHON.start_machine()
    PYTHON.alert("shutting down", level='v')
    PYTHON.exit()
    