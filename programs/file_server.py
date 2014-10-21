import machinelibrary
import defaults
NO_ARGS = defaults.NO_ARGS
NO_KWARGS = defaults.NO_KWARGS
INTERPRETER = ("interpreter.Shell_Service", NO_ARGS, NO_KWARGS)
SHELL = ("interpreter.Shell", NO_ARGS, NO_KWARGS)
FILE_TRANSFER_UTILITY = ("file_transfer_utility.File_Transfer_Utility", NO_ARGS, NO_KWARGS)

defaults.Shell["startup_definitions"] = open("test_script.py", "r").read()
defaults.System["startup_processes"] += (INTERPRETER, SHELL, FILE_TRANSFER_UTILITY)
machine = machinelibrary.Machine()

if __name__ == "__main__":
    machine.run()