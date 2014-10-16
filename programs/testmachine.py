import machinelibrary
import defaults
NO_ARGS = defaults.NO_ARGS
NO_KWARGS = defaults.NO_KWARGS

INTERPRETER_SERVICE = ("interpreter.Shell_Service", NO_ARGS, NO_KWARGS)
CONNECTION = ("interpreter.Shell", NO_ARGS, NO_KWARGS)
defaults.System["startup_processes"] += (INTERPRETER_SERVICE, CONNECTION)
test_machine = machinelibrary.Machine()

if __name__ == "__main__":
    test_machine.run()