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
        for name, value in attributes.items():
            if getattr(value, "dont_save", None):
                attributes[name] = None
                continue
   #         print "Testing if {}.{} ({} {}) is serializable".format(_object, name, type(value), value)
            try:
                json.dumps(value)
            except TypeError:
                if hasattr(value, "instance_name"):
                    attributes[value] = value.__getstate__()
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
        saved = [module + '.' + name, attributes]
        return saved
        
if __name__ == "__main__":
    import mpre._metapython
    m = mpre._metapython.Metapython()
    s = json.dumps(m, cls=Base_Encoder)