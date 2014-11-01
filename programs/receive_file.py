#   mpf.receive_file - receives a file and saves it under the supplied filename
#
#    Copyright (C) 2014  Ella Rose
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import machinelibrary
import defaults
from base import Event
from default_processes import *

try:
    filename = sys.argv[1]
except:
    print "Usage: python receive_file.py filename [interface] [host_port]"
    sys.exit()
try:
    interface = sys.argv[2]
    port = sys.argv[3]
    options = {"address" : (interface, int(port))}
except:
    options = {}
    
defaults.File_Manager["network_chunk_size"] = 32768
defaults.System["startup_processes"] += (FILE_MANAGER, )
machine = machinelibrary.Machine()
Event("File_Manager0", "receive_file", filename, **options).post()
machine.run()