import json

decoder = json.JSONDecoder()


def save_stream(*args):
    return ' '.join(json.dumps(arg) for arg in args)
    
def load_stream(serialized_data):
    result = []
    backup = serialized_data[:]
    count = index = 0
    while serialized_data:
        json_data, end_of_json_data = decoder.raw_decode(serialized_data)
        index += end_of_json_data
        count += 1
        result.append(json_data)  
        serialized_data = backup[index + count:]        
    return result
    
if __name__ == "__main__":
    import pprint
    test_dictionary = {"bool" : True, "int" : 10, "str" : 'test_string', 
                   "float" : 3.14, "tuple" : ("test", "tuple"), 
                   "list" : ["list", "test"], "dict" : {"dictionary" : "test"}}
                   
    stream = save_stream(test_dictionary, test_dictionary, test_dictionary)
    pprint.pprint(load_stream(stream))