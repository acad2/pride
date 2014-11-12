#   mpf.play_wav_file - play a .wav file from disk

import vmlibrary
import defaults
import sys
from default_processes import *

defaults.System["startup_processes"] += (AUDIO_MANAGER, )
machine = vmlibrary.Machine()

try:
    filename = sys.argv[1]
except:
    filename = "test_wav.wav"
    
wav_file = machine.create("audiolibrary.Wav_File", filename=filename)
info = {"rate" : wav_file.rate, "channels" : wav_file.channels, "name" : filename, "format" : wav_file.format}

vmlibrary.base.Event("Audio_Manager0", "play_file", info, wav_file).post()

if __name__ == "__main__":
    machine.run()