import pride
import pride.utilities

def load(saved_data):
    """ usage: load([attributes], [_file]) => restored_instance, attributes
    
        Loads state preserved by the persistence.save method. Loads an instance from either
        a bytestream or file, as returned by the save method.""" 
    attributes = pride.objects["->User"].load_data(saved_data)
    
    print "Performed authenticated load of: ", attributes
    if "_required_modules" in attributes:
        _required_modules = []
        incomplete_modules = attributes["_required_modules"]
        class_name = incomplete_modules.pop()
        module_sources = dict((module_name, source) for module_name, source, none in 
                              incomplete_modules)

        for module_name, source, none in incomplete_modules:
            module = create_module(module_name, source)
            _required_modules.append((module_name, source, module))       
        
        self_class = getattr(module, class_name)
        attributes["_required_modules"] = _required_modules        
    else:
        module_name, class_name = attributes["_required_module"]
        module = importlib.import_module(module_name)
        self_class = getattr(module, class_name)            
    self = self_class.__new__(self_class)
    return self, attributes