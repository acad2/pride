import operator
import json

class Base_Encoder(json.JSONEncoder):
    
    def default(self, _object):
        print "encoding: ", _object
        try:
            print "Ojbect getstate: ", _object.__getstate__
            attributes = _object.__getstate__()
        except AttributeError:
            attributes = _object.__dict__.copy()
        #print "attributes: ", attributes
        objects = attributes.pop("objects", {})
        saved_objects = {}
        for key, value in objects.items():
            saved_objects[key] = [self.default(item) for item in sorted(value,
                                  key=operator.attrgetter("instance_name"))]
                                  
        builtins = dir(__builtins__)
        for name, value in attributes.items():
            print "Testing if {}.{} ({} {}) is serializable".format(_object, name, type(value), value)
            try:
                json.dumps(value)
            except TypeError:
                if hasattr(value, "instance_name"):
                    attributes[value] = value.__getstate__()
                else:
                    raise
        return attributes
        
if __name__ == "__main__":
    import mpre._metapython
    m = mpre._metapython.Metapython()
    s = json.dumps(m, cls=Base_Encoder)