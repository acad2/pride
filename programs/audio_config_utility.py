import machinelibrary
import base

NO_ARGS, NO_KWARGS = machinelibrary.defaults.NO_ARGS, machinelibrary.defaults.NO_KWARGS

machine = machinelibrary.Machine()

base.Event("System0", "create", "audiolibrary.Audio_Configuration_Utility", exit_when_finished=True).post()

if __name__ == "__main__":
    machine.run()
