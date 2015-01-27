from base import Instruction, Base

constructor = Base()

options = {"parse_args" : True,
           "exit_when_finished" : True}
download = constructor.create("networklibrary2.Download", **options)

#Instruction("Asynchronous_Network", "create", "networklibrary2.Download", **options).execute()
