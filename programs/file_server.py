#   mpf.file_server - provide asynchronous uploads for networklibrary.Downloads
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
import defaults
from default_processes import *

defaults.Event_Handler["idle_time"] = 0
defaults.System["startup_processes"] += (FILE_MANAGER, SHELL_SERVICE)
machine = machinelibrary.Machine()

if __name__ == "__main__":
    machine.run()