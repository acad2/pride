#!/usr/bin/env python
""" Launcher script for the Python Runtime and Integrated Development Environment. 
    This script starts a python session, and the first positional argument supplied is
    interpreted as the filepath of the python script to execute. ."""
from __future__ import unicode_literals
import pride.user

if __name__ == "__main__":
    keywords = {"encryption_key" : b'', "mac_key" : b'', 
                "file_system_key" : b'', "salt" : b'', "parse_args" : True}
    while True:
        user = pride.user.User(**keywords)
        # invoke will create it as it's own root object, not a child of User
        python = invoke(user.launcher_type, parse_args=True)
        
        #print "Starting machine"
        try:
            python.start_machine()                
        except SystemExit as error:
            pride.objects["->Finalizer"].run()
            if error.code == "Restart":
                if user.objects["Shell"]:
                    for child in user.objects["Shell"]:
                        child.delete()
                python.delete()
                del python
            else:
                raise              
        # this point is reached if restart() is called. 
        # keeping the keys means login isn't required just for
        # restarting; it also saves some cpu cycles by not having to 
        # reperform the crypto to derive the keys.
        keywords.update({"encryption_key" : user.encryption_key, "mac_key" : user.mac_key, 
                         "file_system_key" : user.file_system_key, "salt" : user.salt,
                         "username" : user.username})        
        user.delete()
        del user
        