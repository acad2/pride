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
from base import Instruction
import defaults
import utilities
options = utilities.get_options(defaults.Outbound_Connection)
Instruction("System", "create", "networklibrary.Outbound_Connection", **options).execute()

if __name__ == "__main__":
    from metapython import Metapython
    metapython = Metapython()
