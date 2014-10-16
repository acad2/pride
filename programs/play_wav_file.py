import machinelibrary
import defaults
import sys

NO_ARGS = defaults.NO_ARGS
NO_KWARGS = defaults.NO_KWARGS

defaults.System["startup_processes"] += ("audiolibrary.Audio_Manager", NO_ARGS, NO_KWARGS), 
machine = machinelibrary.Machine()

try:
    filename = sys.argv[1]
except:
    filename = "test_wav.wav"
machinelibrary.base.Event("Audio_Manager0", "play_wav_file", filename).post()

if __name__ == "__main__":
    machine.run()