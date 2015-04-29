import mpre

Instruction = mpre.Instruction

options = {"parse_args" : True,
           "startup_definitions" : ''}

# feel free to customize
definitions = \
r"""import base

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
    
#proxy = constructor.create("network2.Tcp_Service_Proxy", port=39999)
#import network2
#rpc = network2.Remote_Procedure_Call("Interpreter_Service", "login", ("127.0.0.1", 39999), 
#                                     "root2 password")
#connection = rpc.execute()  

#Instruction("Metapython", "create", "mpre.fileio.File_System").execute()
f = constructor.create("mpre.fileio.File", "test.disk", file_system="virtual")
fs = get_component("File_System")
ftest = fs.get_file("virtual\\test.disk")

#d = constructor.create("mpre.fileio.Directory", path=".\\test\\testdirectory", #file_system="virtual")
"""

options["startup_definitions"] += definitions

if __name__ == "__main__":
    Instruction("Metapython", "create", "metapython.Shell", **options).execute()