#   mpf.play_wav_file - play a .wav file from disk

import sys

import mpre.base as base
import audiolibrary
Instruction = base.Instruction

def metapython_main():
    constructor = base.Base()
    try:
        filename = sys.argv[2]
    except IndexError:
        filename = "testrecording.wav"
    wav_file = constructor.create(audiolibrary.Wav_File, filename=filename, mode='rb')
    info = {"rate" : wav_file.rate, "channels" : wav_file.channels, "name" : filename, "format" : wav_file.format}
    

    Instruction("System", "create", audiolibrary.Audio_Manager).execute()
    Instruction("Audio_Manager", "play_file", info, wav_file).execute()

if __name__ == "__main__":
    metapython_main()