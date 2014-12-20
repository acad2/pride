from base import Event

options = {"parse_args" : True}
Event("System", "create", "networklibrary.File_Server", **options).post()
