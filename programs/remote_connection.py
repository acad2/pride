import machinelibrary
import sys
import defaults

NO_ARGS, NO_KWARGS = tuple(), dict()
try:
    host = sys.argv[1]
    port = sys.argv[2]
except IndexError:
    host = raw_input("Enter host name: ")
    port = raw_input("Enter port: ")
print "Attempting connection to %s:%s" % (host, port)

options = {"host_name" : host,
           "port" : int(port)}
defaults.System["startup_processes"] += ("interpreter.Shell", NO_KWARGS, options),
machine = machinelibrary.Machine()

if __name__ == "__main__":
    machine.run()