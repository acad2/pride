#   mpf.send_file - sends a file via udp to the specified address

import sys
import vmlibrary
import defaults
import utilities
from base import Event
from default_processes import *

file_server_args = dict(defaults.File_Server)
file_server_args.update({"exit_when_finished" : 1})
                         
send_args = {"filename" : None,
             "ip" : "localhost", 
             "port" : 40021}
             
args = dict(file_server_args)
args.update(send_args)
description = "Sends a file to a machine running receive_file.py"
options = utilities.get_options(args, description=description)

file_server_options = dict((key, options[key]) for key in file_server_args.keys())
send_options = dict((key, options[key]) for key in send_args.keys())

Event("System0", "create", "networklibrary.File_Server", **file_server_options).post()
Event("File_Server0", "send_file", **send_options).post()
machine = vmlibrary.Machine()

if __name__ == "__main__":
    machine.run()