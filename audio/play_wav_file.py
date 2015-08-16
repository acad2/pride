import sys

import mpre
import mpre.base as base
import mpre.audio.audiolibrary as audiolibrary
Instruction = mpre.Instruction

constructor = base.Base()

if __name__ == "__main__":
    wav_file = constructor.create(audiolibrary.Wav_File, parse_args=True, mode='rb')
    mpre.audio.enable())
    Instruction("Audio_Input", "play_file", wav_file).execute()