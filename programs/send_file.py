#   mpf.send_file - sends a file via udp to the specified address

import sys
import machinelibrary
import defaults
from base import Event
from default_processes import *

try:
    filename = sys.argv[1]
    ip = sys.argv[2]
except:
    print "Usage: python send_file filename destination_ip destination_port"
    sys.exit()
    
try:
    port = int(sys.argv[3])
except:
    port = 40021
    
defaults.File_Manager["network_chunk_size"] = 8096
defaults.System["startup_processes"] += (FILE_MANAGER, )
machine = machinelibrary.Machine()
Event("File_Manager0", "send_file", filename, ip, port).post()
machine.run()