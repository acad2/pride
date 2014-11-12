import vmlibrary
import defaults
import utilities
from default_processes import *
from base import Event

args = dict(defaults.File_Server)
args.update({"throttle" : .005})

options = utilities.get_options(args)
throttle = options.pop("throttle")

Event("System0", "create", "utilities.File_Server", **options).post()
defaults.Event_Handler["idle_time"] = throttle
machine = vmlibrary.Machine()

if __name__ == "__main__":
    machine.run()