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
import vmlibrary
import defaults
import utilities
from base import Event
from default_processes import *

receive_args = {"filename" : None,
                "interface" : "0.0.0.0",
                "port" : 40021}
server_args = dict(defaults.File_Service)
server_args.update({"exit_when_finished" : 1})

args = dict(receive_args)
args.update(server_args)
options = utilities.get_options(args, description="Receives a file sent from send_file.py")

receive_options = dict((key, options[key]) for key in receive_args.keys())
server_options = dict((key, options[key]) for key in server_args.keys())
machine = vmlibrary.Machine()

Event("System", "create", "networklibrary2.File_Service", **server_options).post()
Event("File_Service0", "receive_file", **receive_options).post()

if __name__ == "__main__":
    machine.run()