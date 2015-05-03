import mpre

Instruction = mpre.Instruction

options = {"parse_args" : True,
           "startup_definitions" : ''}

# feel free to customize
definitions = \
r"""import mpre.base as base
import mpre

constructor = base.Base()
environment = constructor.environment
components = mpre.components
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
    
#f = constructor.create("mpre.fileio.File", "virtual\\test_directory\\test.disk")
fs = get_component("File_System")
#ftest = fs.get_file("virtual\\test_directory\\test.disk")

#d = constructor.create("mpre.fileio.Directory", path=".\\test\\testdirectory", #file_system="virtual")

#e = constructor.create("mpre.fileio.Encrypted_File", "virtual\\test_file.txt")
#e.write("This is a test string. ")
#e.write("And this is another.")
#e.seek(0)
#print e.read()

#_package = constructor.create("mpre.package.Package", mpre)
#with open("metapython.pack", 'wb') as package_file:
#    _package.save(_file=package_file)

#_sqlite3 = _package.get_module("sqlite3")
 
"""

options["startup_definitions"] += definitions

if __name__ == "__main__":
    Instruction("Metapython", "create", "_metapython.Shell", **options).execute()