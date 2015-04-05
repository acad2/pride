import sys

import mpre
import mpre.base as base
import mpre.audio.audiolibrary as audiolibrary
Instruction = mpre.Instruction

constructor = base.Base()

if __name__ == "__main__":
    wav_file = constructor.create(audiolibrary.Wav_File, parse_args=True, mode='rb')
    enable_audio = Instruction("Metapython", "create", audiolibrary.Audio_Manager)
    play_file = Instruction("Audio_Input", "play_file", wav_file)
    enable_audio.execute()
    play_file.execute()