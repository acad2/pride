from base import Event

options = {"parse_args" : True}

# feel free to customize
definitions = ''
options["startup_definitions"] = definitions

Event("System", "create", "metapython.Shell", **options).post()