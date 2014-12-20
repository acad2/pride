from base import Event

options = {"parse_args" : True}
Event("Asynchronous_Network", "create", "networklibrary.Download", **options).post()

if __name__ == "__main__":
    import metapython
    interpreter = metapython.Metapython(parent=__name__)