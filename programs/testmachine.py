#   mpf.testmachine - a virtual machine with a local interpreter connection

import machinelibrary
import defaults
from default_processes import *
from base import Event

machine = machinelibrary.Machine()
Event("System0", "create", "interpreter.Shell_Service").post()
Event("System0", "create", "interpreter.Shell").post()

if __name__ == "__main__":
    machine.run()