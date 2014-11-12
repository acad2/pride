import sys

import vmlibrary
from utilities import get_arguments
from base import Event

description = "Launches a Shell session with the source code from the supplied filename"
argument_info = {"file" : "testscript.py",
                 "ip" : "localhost",
                 "port" : 40000}
arguments = get_arguments(argument_info, description=description)
try:
    source = open(arguments.file, "r").read()
except IOError:
    print "Usage: python launcher.py -(-f)ile source_file -(-i)p target_ip -(-p)ort target_port"
    sys.exit()
    
options = {"startup_definitions" : source,
           "host_ip" : arguments.ip,
           "port" : arguments.port}
machine = vmlibrary.Machine()
Event("System0", "create", "interpreter.Shell_Service").post()
Event("System0", "create", "interpreter.Shell", **options).post()           

if __name__ == "__main__":
    machine.run()