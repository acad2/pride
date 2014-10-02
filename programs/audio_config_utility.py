import machinelibrary
import base

NO_ARGS, NO_KWARGS = machinelibrary.defaults.NO_ARGS, machinelibrary.defaults.NO_KWARGS

machine = machinelibrary.Machine()
system = machine.objects["System"][0]
event = base.Event("System0", "create", "audiolibrary.Audio_Configuration_Utility", 
component=system, exit_when_finished=True).post()

if __name__ == "__main__":
    machine.run()
