#   mpf.remote_connection - connect to another virtual machines interpreter service
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

import machinelibrary
import sys
import defaults

NO_ARGS, NO_KWARGS = tuple(), dict()
try:
    host = sys.argv[1]
    port = sys.argv[2]
except IndexError:
    host = raw_input("Enter host name: ")
    port = raw_input("Enter port: ")
print "Attempting connection to %s:%s" % (host, port)

options = {"host_name" : host,
           "port" : int(port)}
defaults.System["startup_processes"] += ("interpreter.Shell", NO_KWARGS, options),
machine = machinelibrary.Machine()

if __name__ == "__main__":
    machine.run()