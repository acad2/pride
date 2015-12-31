import operator
import json

class Base_Encoder(json.JSONEncoder):
    
    def default(self, _object):
  #      print "encoding: ", _object
        try:
            attributes = _object.__getstate__()
        except AttributeError:
            attributes = _object.__dict__.copy()
        #print "attributes: ", attributes
        objects = attributes.pop("objects", {})
        saved_objects = {}
        already_found = []
        for key, values in objects.items():
            saved_objects[key] = [self.default(item) for item in sorted(values,
                                  key=operator.attrgetter("reference"))
                                  if not item.dont_save]
            already_found.extend(values)
        
        builtins = dir(__builtins__)
        attributes_serialized = []
        references = {}
        
        for name, value in attributes.items():
            if getattr(value, "dont_save", None):
                attributes[name] = None
                continue
            elif value in already_found:
                _reference = value.reference
                references[name] = _reference
                attributes[value] = "reference_{}".format(_reference)
            else:
                try:
                    json.dumps(value)
                except TypeError:
                    if hasattr(value, "reference"):
                        attributes[value] = self.default(value)
                        attributes_serialized.append(name)
                    else:
                        raise
        attributes["objects"] = saved_objects
        return (_object.__module__ + '.' + _object.__class__.__name__,
                attributes_serialized, references, attributes)
        
 

def base_decoder(loaded_json):
  #  print "item length: ", len(loaded_json)
   # print loaded_json
    type_name, serialized_attributes, references, attributes = loaded_json
    print "\nLoading: {}".format((type_name, serialized_attributes, references, attributes))
    for key in serialized_attributes:
        attributes[key] = base_decoder(attributes[key])
    
    loaded_objects = {}
    for _instance_type, values in attributes["objects"].items():
        loaded_objects[_instance_type] = [base_decoder(serialized_instance) for
                                          serialized_instance in values]
    attributes["objects"] = loaded_objects
    instance_type = resolve_string(type_name)
    instance = instance_type.__new__(instance_type)
    
    instance.on_load(attributes)
    print "Loaded: ", instance, '\n', '-' * 80
    return instance
    
if __name__ == "__main__":
    import pride.interpreter
    m = pride.interpreter.Python()
    s = json.dumps(m, cls=Base_Encoder)
    base_decoder(json.loads(s))