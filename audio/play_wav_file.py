#   mpf.play_wav_file - play a .wav file from disk

import base
from base import Instruction

constructor = base.Base()
filename = "testrecording.wav"

wav_file = constructor.create("audiolibrary.Wav_File", filename=filename)
info = {"rate" : wav_file.rate, "channels" : wav_file.channels, "name" : filename, "format" : wav_file.format}

Instruction("System", "create", "audiolibrary.Audio_Manager").execute()
Instruction("Audio_Manager", "play_file", info, wav_file).execute()
