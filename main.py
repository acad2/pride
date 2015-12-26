#!/usr/bin/env python
""" Launcher script for the Python Runtime and Integrated Development Environment. 
    This script starts a python session, and the first positional argument supplied is
    interpreted as the filepath of the python script to execute. ."""
from __future__ import unicode_literals
import pride.user

if __name__ == "__main__":
    pride.user.User(parse_args=True)