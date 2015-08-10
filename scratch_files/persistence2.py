import collections
import json

import ast

LITERALS = [int, float, long, complex,
            str, unicode, bytes, 
            list, tuple,
            type(None), bool,
            set, dict]
                    
def serialize_object(_object):
    object_type = type(_object)
    is_literal = object_type in LITERALS
    if is_literal:
        if object_type == dict:
            _object = serialize_dictionary(_object)
        state = _object
    else:
        try:
            state = (object_type.__name__, _object.__module__,
                     serialize(_object.__getstate__()))
        except AttributeError:
            state = (object_type.__name__, _object.__module__, 
                     serialize_dictionary(_object.__dict__))
    return state
 
def dispatch(value):
    value_type = type(value)
    serialized = False
    if value_type not in LITERALS:
        value = serialize_object(value)
        serialized = True
    elif value_type == dict:
        value = serialize_dictionary(value)
        serialized = True
    elif value_type in (list, tuple, set):        
        value = serialize_iterable(value)
        serialized = True
    return serialized, value
    
def serialize_dictionary(dictionary):
    dictionary_info = {}
    serialized_keys = []
    for key, value in dictionary.items():  
        serialized, value = dispatch(value)
        dictionary_info[key] = value
        if key == "tuple":
            print "Set tuple to: ", type(value), value
        if serialized:
            serialized_keys.append(key)
    if serialized_keys:
        dictionary_info["__serialized_keys"] = serialized_keys
    return dictionary_info
  
def serialize_iterable(iterable):
    serialized_items, new_iterable = [], []
    for index, item in enumerate(iterable):
        serialized, item = dispatch(item)
        new_iterable.append(item)
        if serialized:
            serialized_item.append(index)
     
    return type(iterable)(new_iterable) #serialized_items, new_iterable    
    
def serialize(py_object):
    return json.dumps(serialize_object(py_object))
    
def deserialize(serialized_object):
    try:
        class_name, module_name, attributes = json.loads(serialized_object)
    except ValueError: 
        result = json.loads(serialized_object)
    else:
        module = importlib.import_module(module_name)
        result = getattr(module, class_name)
        for key, value in attributes.items():
            setattr(result, key, value)
    return result        
        
if __name__ == "__main__":
    test_dictionary = {"bool" : True, "int" : 10, "str" : 'test_string', 
                       "float" : 3.14, "tuple" : ("test", "tuple"), 
                       "list" : ["list", "test"], "dict" : {"dictionary" : "test"}}
    serialized = serialize(test_dictionary)
    print serialized
    assert test_dictionary == deserialize(serialized)
    
    import base
    base_object = base.Base(**test_dictionary)
    test_dictionary["complex_object"] = base_object
    serialized_again = serialize(test_dictionary)
    print test_dictionary
    print '\n', deserialize(serialized_again)
    assert test_dictionary == deserialize(serialized_again)
    
    serialized_object = serialize(base_object)
    assert base_object == deserialize(serialized_object)