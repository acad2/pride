import sys

import pride
import pride.base as base
import pride.audio.audiolibrary as audiolibrary
Instruction = pride.Instruction

constructor = base.Base()

if __name__ == "__main__":
    wav_file = constructor.create(audiolibrary.Wav_File, parse_args=True, mode='rb')
    pride.audio.enable())
    Instruction("/Python/Audio_Input", "play_file", wav_file).execute()