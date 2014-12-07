import sys

import defaults
from utilities import get_options
from base import Event

description = "Launches a Shell session and executes the source code from the supplied filename"
options = get_options(defaults.Shell, description=description)

# feel free to customize
definitions = ''
options["startup_definitions"] += definitions

Event("System", "create", "metapython.Shell", **options).post()