__all__ = []#"_export"]#, "_improt"]

from socket import gethostbyname as get_ip_address

import importlib
import inspect
import os

import pride

def _export(*args):
    """ Usage: export module_name for fqdn as module_name
        
        Executes the module on the host named by fqdn.
        Requires shell credentials and a running instance of pride on the target machine.
        The as clause is optional"""
    try:
        module_name, for_fqdn, as_name = args
    except ValueError:
        module_name, for_fqdn = args
        as_name = module_name
    fqdn = for_fqdn[1]
    as_name = as_name[1]
    
    if pride.compiler.find_module(module_name, None):
        module_source = pride.compiler.module_source[module_name][0]
    else:
        raise ValueError("Unable to find module {}".format(module_name))
    
    ip = get_ip_address(fqdn)      
    for shell in pride.objects["/User"].objects["Shell"]:
        if shell.ip == ip:
            shell.handle_input(module_source)
            break
    else:
        pride.objects["/User"].create("pride.interpreter.Shell", ip=ip, 
                                       startup_definitions=module_source)
                  
def _improt(module_name):        
    """ Usage: improt module_name
    
        Silently delete the .py file that contains the source for module_name.        
        (It's a joke; not to be taken seriously)"""
    module = __import__(module_name)    
    filename = inspect.getfile(module)    
    os.remove(filename)
    if filename[-1] == 'c':
        os.remove(filename[:-1])
    