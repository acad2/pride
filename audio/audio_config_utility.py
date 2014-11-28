#  mpf.audio_config_utility - create config file for audiolibrary.audio_manager

import vmlibrary
import defaults
from default_processes import *

defaults.Audio_Configuration_Utility["exit_when_finished"] = True
defaults.System["startup_processes"] += (AUDIO_CONFIGURATION_UTILITY, )
machine = vmlibrary.Machine()

if __name__ == "__main__":
    machine.run()
