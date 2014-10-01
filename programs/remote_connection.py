import machinelibrary
import sys

NO_ARGS, NO_KWARGS = tuple(), dict()
try:
    host_name = sys.argv[1]
    port = sys.argv[2]
except IndexError:
    host_name = raw_input("Enter host name: ")
    port = raw_input("Enter port: ")
print "Attempting connection to %s:%s" % (host_name, port)
COMPONENTS = (("eventlibrary.Event_Handler", NO_ARGS, NO_KWARGS),
("networklibrary.Network_Manager", NO_ARGS, NO_KWARGS),
("systemlibrary.Idle", NO_ARGS, NO_KWARGS), 
("interpreter.Shell", NO_ARGS, {"host_name" : host_name, "port" : int(port)}))
SYSTEM_CONFIGURATION = (("systemlibrary.System", NO_ARGS, {"component_configuration" : COMPONENTS}), )

machine = machinelibrary.Machine(system_configuration=SYSTEM_CONFIGURATION)

if __name__ == "__main__":
    machine.run()