def import_change(module_name):
    try:
        importlib.import_module(module_name)
    except ImportError:
        if module_name in rebind_names:
            return rebind_names[module_name]
            
from mpre.misc.decoratorlibrary import Timed

def test(method_names):
    times = []
    string = "{: >20} time: {: >20}"
    for method_name in method_names:
        time, result = Timed(locals()[method_name])()
        times.append(string.format(method_name, time))            