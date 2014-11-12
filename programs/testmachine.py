#   mpf.testmachine - a virtual machine with a local interpreter connection

import vmlibrary
import defaults
from default_processes import *
from base import Event

machine = vmlibrary.Machine()
Event("System0", "create", "interpreter.Shell_Service").post()
Event("System0", "create", "interpreter.Shell").post()

if __name__ == "__main__":
    machine.run()