#   mpf.capture_live_audio - records a .wav from the microphone
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

import vmlibrary
import defaults
from default_processes import *

#defaults.Audio_Manager["config_file_name"] = "audiocfg"
defaults.Audio_Input["record_to_disk"] = True
defaults.System["startup_processes"] += (AUDIO_MANAGER, ) 

machine = vmlibrary.Machine()

if __name__ == "__main__":
    machine.run()