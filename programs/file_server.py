import vmlibrary
import defaults
import utilities
from default_processes import *
from base import Event

args = dict(defaults.File_Server)
args.update({"throttle" : .005})

options = utilities.get_options(args)
throttle = options.pop("throttle")

Event("System", "create", "networklibrary.File_Server", **options).post()
machine = vmlibrary.Machine()

if __name__ == "__main__":
    machine.run()