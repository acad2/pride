import base
Instruction = base.Instruction

options = {"parse_args" : True,
           "startup_definitions" : ''}

# feel free to customize
definitions = \
"""import base

def buffer_data(connection, data):
    Instruction("Asynchronous_Network", "buffer_data", connection, data).execute()

def add_to_network(sock):
    Instruction("Asynchronous_Network", "add", sock).execute()

def remove_from_network(sock):
    Instruction("Asynchronous_Network", "remove", sock).execute()

def add_network_service(address, name):
    Instruction("Service_Listing", "add_service", address, name).execute()

def print_components(mode="keys", size=(None, )):
    _slice = slice(*size)
    print getattr(base.Component_Resolve, mode)()[_slice]

def get_component(instance_name):
    return base.Component_Resolve[instance_name]

constructor = base.Base()
create = constructor.create

def delete(instance_name='', instance=None):
    if instance_name:
        Instruction(instance_name, "delete").execute()
    elif instance:
        instance.delete()
        
def test():
    Instruction("System", "create", "securitylibrary.DoS", target=("192.168.1.254", 80)).execute()
    delete = Instruction("DoS", "delete")
    delete.priority = 10
    delete.execute()"""

options["startup_definitions"] += definitions

Instruction("System", "create", "metapython.Shell", **options).execute()
