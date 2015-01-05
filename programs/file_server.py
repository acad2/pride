from base import Event

options = {"parse_args" : True}
Event("System", "create", "networklibrary2.File_Service", **options).post()
