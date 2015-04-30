import importlib
import os
import sys
import inspect
import mpre.utilities as utilities
import mpre._compile
import mpre.fileio
import mpre.importers

startup_modules = ["mpre." + module_name for module_name 
                   in ("defaults", "metaclass", "base", "network", 
                       "_metapython", "shell_launcher", "utilities", "importers")]
required_modules = ["sys", "os", "types", "pickle", "importlib"]
#embed_objects = [utilities, mpre.importers]
LAUNCHER_FILENAME = "exelauncher.py"

def build_launcher(from_modules):
    with open(LAUNCHER_FILENAME, 'w+') as launcher:
        imports = r''
        for module in required_modules:
            imports += "import {}\n".format(module)
        launcher.write(imports)
        
        encrypted_file = mpre.fileio.Encrypted_File(os.path.sep.join(("virtual",     
                                                                      LAUNCHER_FILENAME)))
        _file = encrypted_file.file
        """embedded_string = r''
        for embedded_object in embed_objects:
            print "Encrypting and embedding: ", embedded_object
            encrypted_file.write(inspect.getsource(embedded_object))
            _file.seek(0)
            embedded_string += "{}\n\n".format(_file.read())
            _file.truncate(0)
        launcher.write(embedded_string)"""
        
        add_module = r"Encrypted_String_Importer.add_module('{}', {}_source)" + "\n\n"
        for module_name in from_modules:
            _module_name = module_name.replace('.', '_')
            importlib.import_module(module_name)
            print "Embedding and encrypting module: ", module_name
            encrypted_file.write(inspect.getsource(sys.modules[module_name]))
            _file.seek(0)
            encrypted_source = _file.read()
           # print "Got encrypted source", encrypted_source
            encrypted_file.truncate(0)
            launcher.write("{}_source = r'''{}'''\n\n".format(_module_name, encrypted_source))
            launcher.write(add_module.format(module_name, _module_name))
        launcher.write("sys.meta_path = [Encrypted_String_Importer()]\n\n")
        launcher.write("Encrypted_String_Importer.key = r'''{}'''".format(encrypted_file.key))
        launcher.write("\n\nif __name__ == '__main__':\n")
        launcher.write("    import mpre._metapython\n")
        launcher.write("    metapython = mpre._metapython.Metapython(parse_args=True)\n")
        launcher.write("    metapython.start_machine()")
        launcher.flush()
        mpre._compile.py_to_compiled([LAUNCHER_FILENAME], 'exe')
        
if __name__ == "__main__":
    build_launcher(startup_modules)
    #os.remove(LAUNCHER_FILENAME)