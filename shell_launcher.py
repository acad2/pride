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

def print_components(mode="keys", size=(None, )):
    _slice = slice(*size)
    print getattr(constructor.environment.Component_Resolve, mode)()[_slice]

def get_component(instance_name):
    return constructor.environment.Component_Resolve[instance_name]

def delete(instance=None):
    Instruction(getattr(instance, "instance_name", instance), "delete").execute()
                    
def build_docs(site_name=''):
    site_name = site_name if site_name else raw_input("Please enter site name: ")
    
    Instruction("Metapython", "create", "mpre.docbuilder.Documentation_Builder",
                 site_name=site_name).execute()
                 
def update(component):
    return constructor.parallel_method(component, "update")  
    

d = get_component("Metapython").create("mpre.misc.securitylibrary.DoS", target=("192.168.1.254", 80), display_latency=True)
#Instruction("DoS", "delete").execute(2)
#Instruction("Metapython", "exit").execute(2)
#Instruction("Processor", "pause", "DoS").execute(1)
"""

options["startup_definitions"] += definitions

if __name__ == "__main__":
    Instruction("Metapython", "create", "metapython.Shell", **options).execute()