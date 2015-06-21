import mpre

options = {"parse_args" : True,
           "startup_definitions" : ''}

# feel free to customize
definitions = \
r"""import mpre.base
import mpre

environment = mpre.environment
objects = mpre.objects
from mpre.importers import From_Disk
from mpre.utilities import documentation

__from_disk_importer = From_Disk()
from_disk_import = __from_disk_importer.load_module

#def restart():
    
    
def save(instance_name, _file=None):
    return objects[instance_name].save(_file=None)
    
def create(instance_type, *args, **kwargs):
    return objects["Metapython"].create(instance_type, *args, **kwargs)

def delete(instance_name):
    objects[instance_name].delete()
                                     
def update(instance_name):
    return objects[instance_name].update()
    
#f = create("mpre.fileio.File", "virtual\\test_directory\\test.disk")
#fs = objects["File_System"]
#ftest = fs.get_file("virtual\\test_directory\\test.disk")

#d = create("mpre.fileio.Directory", path=".\\test\\testdirectory", #file_system="virtual")

#e = create("mpre.fileio.Encrypted_File", "virtual\\test_file.txt")
#e.write("This is a test string. ")
#e.write("And this is another.")
#e.seek(0)
#print e.read()

_package = create("mpre.package.Package", mpre, include_documentation=True)
#with open("metapython.pack", 'wb') as package_file:
#    _package.save(_file=package_file)
#print _package.documentation["mpre"].markdown

#_sqlite3 = _package.get_module("sqlite3")
 
#import mpre.gui
#mpre.gui.enable()
#h = objects["SDL_Window"].create("mpre.gui.widgetlibrary.Homescreen")
#t = objects["Task_Bar"]
#i = objects["Indicator"]
##d = objects["Date_Time_Button"]

#import mpre.package
#p = mpre.package.Package(mpre)

#update("Metapython")
#update("Metapython")
#x = objects["Metapython"].save()
#y = mpre.base.Base.load(x) # calls .on_load automatically

#z = s(constructor)
#newz = l(z) # does not call .on_load

sniffer = create("mpre.network.Packet_Sniffer")
"""

options["startup_definitions"] += definitions

if __name__ == "__main__":
    objects["Metapython"].create("_metapython.Shell", **options)