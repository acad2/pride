import ast

LITERALS = [int, float, long, complex,
            str, unicode, bytes, 
            list, tuple,
            type(None), bool,
            set, dict]
            
def serialize_literal(literal):
    if type(literal) == dict:
        result = serialize_dictionary(literal)
    else:
        result = repr(literal)
    return result
    
def load_literal(serialized_dictionary):
    return ast.literal_eval(serialized_dictionary)
    
def serialize_object(_object):
    object_type = type(_object)
    is_literal = object_type in LITERALS
    if is_literal:
        state = serialize_literal(_object)
    else:
        try:
            state = (_object.__class__.__name__, _object.__module__,
                     _object.__getstate__())
        except AttributeError:
            state = (_object.__class__.__name__, _object.__module__, 
                     serialize_dictionary(_object.__dict__))
    return state
    
def serialize_dictionary(dictionary):
    dictionary_info = {}
    for key, value in dictionary.items():
        value_type = type(value)
        if value_type not in LITERALS:
            value = serialize_object(value)
        elif value_type == dict:
            value = serialize_dictionary(value)
        dictionary_info[key] = value        
    return dictionary_info
    
def serialize(py_object):
    return serialize_object(py_object)
    
if __name__ == "__main__":
    test_dictionary = {"bool" : True, "int" : 10, "str" : 'test_string', 
                       "float" : 3.14, "tuple" : ("test", "tuple"), 
                       "list" : ["list", "test"], "dict" : {"dictionary" : "test"}}
    serialized = serialize(test_dictionary)
    print serialized
    
    import base
    base_object = base.Base(**test_dictionary)
    test_dictionary["complex_object"] = base_object
    serialized_again = serialize(test_dictionary)
    
    print serialized_again