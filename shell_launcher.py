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

def delete(instance_name):
    constructor.parallel_method(instance_name, "delete")
                    
def build_docs(**kwargs):    
    return constructor.parallel_method("Metapython", "create", 
                                       "mpre.package.Documentation", **kwargs)
                 
def update(component):
    return constructor.parallel_method(component, "update")
"""

options["startup_definitions"] += definitions

if __name__ == "__main__":
    Instruction("Metapython", "create", "metapython.Shell", **options).execute()