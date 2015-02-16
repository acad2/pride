import base
Instruction = base.Instruction

options = {"parse_args" : True,
           "startup_definitions" : ''}

# feel free to customize
definitions = \
"""import base

constructor = base.Base()
create = constructor.create

def add_to_network(sock):
    constructor.public_method("Asynchronous_Network", "add", sock).execute()

def remove_from_network(sock):
    Instruction("Asynchronous_Network", "remove", sock).execute()

def add_network_service(address, name):
    Instruction("Service_Listing", "add_service", address, name).execute()

def print_components(mode="keys", size=(None, )):
    _slice = slice(*size)
    print getattr(base.Component_Resolve, mode)()[_slice]

def get_component(instance_name):
    return base.Component_Resolve[instance_name]

def processor_usage():
    Instruction("Processor", "display_processor_usage").execute()

def delete(instance_name='', instance=None):
    if instance_name:
        Instruction(instance_name, "delete").execute()
    elif instance:
        instance.delete()
        
def test():
    Instruction("System", "create", "securitylibrary.DoS", target=("192.168.1.254", 80)).execute()
    delete = Instruction("DoS", "delete")
    delete.priority = 1
    delete.execute()

#Instruction("System", "create", "mpre.audio.audiolibrary.Audio_Manager",
           #  use_defaults=True).execute()
            
def build_docs(site_name=''):
    site_name = site_name if site_name else raw_input("Please enter site name: ")
    
    Instruction("System", "create", "mpre.docbuilder.Documentation_Builder",
                 site_name=site_name).execute()

"""

options["startup_definitions"] += definitions
metapython_main = lambda: Instruction("System", "create", "metapython.Shell", **options).execute()

if __name__ == "__main__":
    Instruction("System", "create", "metapython.Shell", **options).execute()