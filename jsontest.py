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
        for key, value in objects.items():
            saved_objects[key] = [self.default(item) for item in sorted(value,
                                  key=operator.attrgetter("instance_name"))
                                  if not item.dont_save]
                                  
        builtins = dir(__builtins__)
        attributes_serialized = []
        for name, value in attributes.items():
            if getattr(value, "dont_save", None):
                attributes[name] = None
                continue
   #         print "Testing if {}.{} ({} {}) is serializable".format(_object, name, type(value), value)
            try:
                json.dumps(value)
            except TypeError:
                if hasattr(value, "instance_name"):
                    attributes[value] = self.default(value)
                    attributes_serialized.append(name)
                else:
                    raise
        attributes["objects"] = saved_objects
   #     for key in attributes.keys():
   #         print _object, key, type(key)
   #         import pprint
   #         pprint.pprint(attributes)
   #         assert isinstance(key, str)
        name = _object.__class__.__name__
        module = _object.__module__
        saved = (module + '.' + name, attributes_serialized, attributes)
        return saved
 

def base_decoder(loaded_json):
  #  print "item length: ", len(loaded_json)
   # print loaded_json
    type_name, serialized_attributes, attributes = loaded_json
 #   print "Loading: {}".format((type_name, serialized_attributes, attributes))
    for key in serialized_attributes:
        attributes[key] = base_decoder(attributes[key])
    
    loaded_objects = {}
    for _instance_type, values in attributes["objects"].items():
        loaded_objects[_instance_type] = [base_decoder(serialized_instance) for
                                          serialized_instance in values]
    attributes["objects"] = loaded_objects
    instance_type = mpre.utilities.resolve_string(type_name)
    instance = instance_type.__new__(instance_type)
    instance.on_load(attributes)
    return instance
    
if __name__ == "__main__":
    import mpre._metapython
    m = mpre._metapython.Metapython()
    s = json.dumps(m, cls=Base_Encoder)
    base_decoder(json.loads(s))