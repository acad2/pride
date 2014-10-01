import machinelibrary

NO_ARGS, NO_KWARGS = machinelibrary.defaults.NO_ARGS, machinelibrary.defaults.NO_KWARGS

CONFIG_UTILITY = ("audiolibrary.Audio_Configuration_Utility", NO_ARGS, {"exit_when_finished" : True})
EVENT_HANDLER = ("eventlibrary.Event_Handler", NO_ARGS, {"get_low_level_events" : False})
IDLE = ("systemlibrary.Idle", NO_ARGS, NO_KWARGS)

COMPONENTS = (CONFIG_UTILITY, EVENT_HANDLER, IDLE)
SYSTEM = ("systemlibrary.System", NO_ARGS, {"component_configuration" : COMPONENTS})
SYSTEM_CONFIGURATION = (SYSTEM, ) # system_configuration needs to be an iterable

machine = machinelibrary.Machine(system_configuration=SYSTEM_CONFIGURATION)

if __name__ == "__main__":
    try:
        machine.run()
    except:
        pass