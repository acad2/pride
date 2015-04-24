import importlib
import sys
import inspect
import mpre.utilities
import mpre._compile

startup_modules = ["defaults", "metaclass", "base", "_metapython", "network", "shell_launcher"]

required_modules = ["sys", "os", "types"]
LAUNCHER_FILENAME = "exelauncher.py"

def build_launcher(from_modules):
    with open(LAUNCHER_FILENAME, 'w+') as launcher:
        imports = ''
        for module in required_modules:
            imports += "import {}\n".format(module)
        launcher.write(imports)
        for module_name in from_modules:
            full_name = "mpre." + module_name
            importlib.import_module(full_name)
            source = inspect.getsource(sys.modules[full_name])
            launcher.write("{}_source = r'''print 'fuck yeah'\n{}'''\n\n".format(module_name, source))
        launcher.write("{}\n\n".format(inspect.getsource(mpre.utilities.create_module)))
        launcher.write("{}\n\n".format(inspect.getsource(mpre.utilities.Importer)))
        launcher.write("sys.meta_path = [Importer()]\n\n")
        launcher.write("if __name__ == '__main__':\n")
        launcher.write("    import mpre._metapython\n")
        launcher.write("    metapython = mpre._metapython.Metapython(parse_args=True)\n")
        launcher.write("    metapython.start_machine()")
        launcher.flush()
  
if __name__ == "__main__":
    build_launcher(startup_modules)
    mpre._compile.py_to_compiled([LAUNCHER_FILENAME], 'exe')