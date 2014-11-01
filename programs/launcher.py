import sys

import machinelibrary
from utilities import get_arguments
from base import Event

description = "Launches a Shell session with the source code from the supplied filename"
argument_names = [("-f", "--file"), ("-i", "--ip"), ("-p", "--port")]
argument_defaults = ["testscript.py", "localhost", 40000]
arguments = get_arguments(argument_names, argument_defaults, description=description)
try:
    source = open(arguments.file, "r").read()
except IOError:
    print "Usage: python launcher.py -(-f)ile source_file -(-i)p target_ip -(-p)ort target_port"
    sys.exit()
    
options = {"startup_definitions" : source,
           "host_ip" : arguments.ip,
           "port" : arguments.port}
machine = machinelibrary.Machine()
Event("System0", "create", "interpreter.Shell", **options).post()           

if __name__ == "__main__":
    machine.run()