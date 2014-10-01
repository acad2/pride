import machinelibrary

NO_ARGS, NO_KWARGS = tuple(), dict()
COMPONENTS = (("interpreter.Shell_Service", NO_ARGS, NO_KWARGS),
("systemlibrary.Idle", NO_ARGS, NO_KWARGS),
("networklibrary.Network_Manager", NO_ARGS, NO_KWARGS),
("eventlibrary.Event_Handler", NO_ARGS, NO_KWARGS),
("audiolibrary.Audio_Manager", NO_ARGS, NO_KWARGS))
SYSTEM = ("systemlibrary.System", NO_ARGS, {"component_configuration" : COMPONENTS})
SYSTEM_CONFIGURATION = (SYSTEM, ) # must be an iterable, even if there's only one

machine = machinelibrary.Machine(system_configuration=SYSTEM_CONFIGURATION)

if __name__ == "__main__":
    try:
        machine.run()
    except IOError:
        print "Please run audio_config_utility"