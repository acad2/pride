from base import Event

options = {"parse_args" : True}
Event("Asynchronous_Network", "create", "networklibrary2.Download", **options).post()
