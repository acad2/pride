#   mpf.default_processes - constants - entries are useful for setting up new vms
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

NO_KWARGS = dict()
NO_ARGS = tuple()

# audiolibrary
AUDIO_MANAGER = ("audiolibrary.Audio_Manager", NO_ARGS, NO_KWARGS)
AUDIO_CONFIGURATION_UTILITY = ("audiolibrary.Audio_Configuration_Utility", NO_ARGS, NO_KWARGS)

# interpreter
SHELL_SERVICE = ("interpreter.Shell_Service", NO_ARGS, NO_KWARGS)
SHELL = ("interpreter.Shell", NO_ARGS, NO_KWARGS)

# utilities
File_Service = ("networklibrary2.File_Service", NO_ARGS, NO_KWARGS)