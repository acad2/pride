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

import mpre.base
import mpre.audio.audiolibrary as audiolibrary
import mpre.audio.utilities as utilities

constructor = mpre.base.Base()

wav_file = constructor.create(audiolibrary.Wav_File, channels=2, rate=48000, 
                              filename="captured_live_audio.wav", mode='wb')

record_instruction = mpre.base.Instruction("Audio_Manager", "record", 
                                           "Microphone", wav_file)

                                      
if __name__ == "__main__":
    mpre.audio.utilities.enable_audio()
    record_instruction.execute()