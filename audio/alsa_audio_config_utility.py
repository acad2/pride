#  mpf.alsa_audio_config_utility - create config file for alsa_audiolibrary.audio_manager

import machinelibrary
import defaults
from default_processes import *
from base import Event

machine = machinelibrary.Machine()

event_info = ("System0", "create", "alsa_audiolibrary.Alsa_Audio_Configuration_Utility")
config_utility_options = {"exit_when_finished" : True}
Event(*event_info, **config_utility_options).post()

if __name__ == "__main__":
    machine.run()
