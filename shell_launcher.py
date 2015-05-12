import mpre

Instruction = mpre.Instruction

options = {"parse_args" : True,
           "startup_definitions" : ''}

# feel free to customize
definitions = \
r"""import mpre.base as base
import mpre

environment = mpre.environment
component = mpre.component
def create(instance_type, *args, **kwargs):
    return component["Metapython"].create(instance_type, *args, **kwargs)

def delete(instance_name):
    component[instance_name].delete()
                                     
def update(instance_name):
    return component[instance_name].update()
    
#f = create("mpre.fileio.File", "virtual\\test_directory\\test.disk")
fs = component["File_System"]
#ftest = fs.get_file("virtual\\test_directory\\test.disk")

#d = create("mpre.fileio.Directory", path=".\\test\\testdirectory", #file_system="virtual")

#e = create("mpre.fileio.Encrypted_File", "virtual\\test_file.txt")
#e.write("This is a test string. ")
#e.write("And this is another.")
#e.seek(0)
#print e.read()

#_package = create("mpre.package.Package", mpre, include_documentation=True)
#with open("metapython.pack", 'wb') as package_file:
#    _package.save(_file=package_file)
#print _package.documentation["mpre"].markdown

#_sqlite3 = _package.get_module("sqlite3")
 
#import mpre.gui.gui as gui
#gui.enable()
#create("mpre.gui.widgetlibrary.Homescreen")
#r = component["Renderer"]
#h = component["Homescreen"]

#import mpre.package
#p = mpre.package.Package(mpre)

#update("Metapython")
#update("Metapython")
#x = component["Metapython"].save()
#y = mpre.base.Base.load(x) # calls .on_load automatically

#z = s(constructor)
#newz = l(z) # does not call .on_load
"""

options["startup_definitions"] += definitions

if __name__ == "__main__":
    Instruction("Metapython", "create", "_metapython.Shell", **options).execute()