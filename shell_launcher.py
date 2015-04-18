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
                 
def update(component="Network"):
    Instruction(component, "update").execute()

m = get_component("Metapython")
pickled_state = m.save()
state = pickle.loads(pickled_state)

m2 = m.load(state)
#m2 = m2.load(state)
"""

options["startup_definitions"] += definitions

if __name__ == "__main__":
    Instruction("Metapython", "create", "metapython.Shell", **options).execute()