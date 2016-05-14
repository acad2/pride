import pprint

import pride
import pride.utilities
import pride.module_utilities

def load(saved_data):
    """ usage: load([attributes], [_file]) => restored_instance, attributes
    
        Loads state preserved by the persistence.save method. Loads an instance from either
        a bytestream or file, as returned by the save method."""
    user = pride.objects["->User"]
    attributes = user.load_data(saved_data)
    repo_id = user.generate_tag(user.username)
    version_control = pride.objects["->Python->Version_Control"]
    _required_modules = []
    module_info = attributes.pop("_required_modules")
    class_name = module_info.pop()
    for module_name, module_id in module_info:
        source = version_control.load_module(module_name, module_id, repo_id)        
        module_object = pride.module_utilities.create_module(module_name, source)
        _required_modules.append((module_name, module_id, module_object))     
    
    self_class = getattr(module_object, class_name)
    attributes["_required_modules"] = _required_modules        
           
    self = self_class.__new__(self_class)
    return self, attributes
    
def test_load():
    user = pride.objects["->User"]
    saved_data = user.save()
    new_self = load(saved_data)
    print id(new_self), id(user)
    raise SystemExit()
    
if __name__ == "__main__":
    test_load()