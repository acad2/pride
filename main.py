#!/usr/bin/env python
""" Launcher script for the Python Runtime and Integrated Development Environment. 
    This script starts a python session, and the first positional argument supplied is
    interpreted as the filepath of the python script to execute. ."""
from __future__ import unicode_literals
import pride.user

if __name__ == "__main__":
    keywords = {"encryption_key" : b'', "mac_key" : b'', 
                "file_system_key" : b'', "salt" : b''}
    while True:
        user = pride.user.User(parse_args=True, **keywords)
        # this point is reached if restart() is called. 
        # keeping the keys means the password isn't required just for
        # restarting; it also saves some cpu cycles by not having to 
        # reperform the crypto to derive the keys.
        keywords.update({"encryption_key" : user.encryption_key, "mac_key" : user.mac_key, 
                         "file_system_key" : user.file_system_key, "salt" : user.salt,
                         "username" : user.username})        
        user.delete()
        