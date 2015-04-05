import mpre

Instruction = mpre.Instruction

options = {"parse_args" : True,
           "startup_definitions" : ''}

# feel free to customize
definitions = \
"""import base

constructor = base.Base()
environment = constructor.environment
    
create = constructor.create

def add_to_network(sock):
    constructor.parallel_method("Network", "add", sock).execute()

def remove_from_network(sock):
    Instruction("Network", "remove", sock).execute()

def add_network_service(address, name):
    Instruction("Service_Listing", "add_service", address, name).execute()

def print_components(mode="keys", size=(None, )):
    _slice = slice(*size)
    print getattr(constructor.environment.Component_Resolve, mode)()[_slice]

def get_component(instance_name):
    return constructor.environment.Component_Resolve[instance_name]

def delete(instance_name='', instance=None):
    if instance_name:
        Instruction(instance_name, "delete").execute()
    elif instance:
        instance.delete()
                    
def build_docs(site_name=''):
    site_name = site_name if site_name else raw_input("Please enter site name: ")
    
    Instruction("Metapython", "create", "mpre.docbuilder.Documentation_Builder",
                 site_name=site_name).execute()

Instruction("Metapython", "save_state").execute()
                 
Instruction("Network", "update").execute()                 
"""

options["startup_definitions"] += definitions

if __name__ == "__main__":
    Instruction("Metapython", "create", "metapython.Shell", **options).execute()