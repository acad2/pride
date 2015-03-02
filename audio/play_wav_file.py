#   mpf.play_wav_file - play a .wav file from disk

import sys

import mpre.base as base
import mpre.audio.audiolibrary as audiolibrary
Instruction = base.Instruction

constructor = base.Base()

if __name__ == "__main__":
    wav_file = constructor.create(audiolibrary.Wav_File, parse_args=True, mode='rb')
    enable_audio = Instruction("Metapython", "create", audiolibrary.Audio_Manager)
    play_file = Instruction("Audio_Manager", "play_file", wav_file)
    enable_audio.execute()
    play_file.execute()