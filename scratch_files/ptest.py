import struct

format_switch = {int : 'q',
                 float : 'd',
                 str : 's',
                 bool : '?'}
   
datasize_switch = {'q' : 8,
                   'd' : 8,
                   's' : 0,
                   '?' : 1}
                   
def pack(*args):
    format_string = get_format_string(*args)            
    return format_string, struct.pack(format_string, *args)  
        
def get_format_string(*args):
    format_string = r''
    for argument in args:
        format_character = format_switch[type(argument)]
        if format_character == 's':
            format_character = str(len(argument)) + 's'
        format_string += format_character
    return format_string
    
def pack_dictionary(dictionary):
    keys = dictionary.keys()
    keys_format, packed_keys = pack(*keys)  
    values_format, packed_values = pack(*(dictionary[key] for key in keys))
        
    data_start = struct.pack('q', 16 + len(keys_format) + len(values_format))
    keys_size = struct.pack('q', len(keys_format))
    
    return (keys_size + data_start +
            keys_format + values_format +
            packed_keys + packed_values)
           
def unpack_dictionary(packed_dictionary):
    keys_size, data_start = struct.unpack("qq", packed_dictionary[:16])
        
    keys_format = packed_dictionary[16:16 + keys_size]
    values_format = packed_dictionary[16 + keys_size:data_start]
        
    key_sizes = [item for item in keys_format.split('s') if item]
    key_sizes = sum((int(item) for item in key_sizes))
    keys = struct.unpack(keys_format, packed_dictionary[data_start:data_start + key_sizes])
    
    values = struct.unpack(values_format, packed_dictionary[data_start + key_sizes:])
    return dict(zip(keys, values))    
        
if __name__ == "__main__":
    string, data = pack(1, 2, 3, 4, 5, 1337.0, 'this is a test string', len('this is a test string'), True)
   # print string, data
    _data = struct.unpack(string, data)
  #  print _data
    
  #  print "dictionary test"
    dictionary = {"testing" : "test string",
                  "test2" : True,
                  "test3" : 10}
    byte_dictionary = pack_dictionary(dictionary)
    print byte_dictionary
    print "\nunpacking"
    print unpack_dictionary(byte_dictionary)