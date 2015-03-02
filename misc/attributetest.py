import mmap
import struct
import ast
import cPickle as pickle

_get_attribute = object.__getattribute__
_set_attribute = object.__setattr__

class Struct(object):
   
    format_switch = {int : 'q',
                     float : 'd',
                     str : 's',
                     bool : '?'}
    
    format_size = {'q' : 8,
                   'd' : 8,
                   's' : 0,
                   '?' : 1}
    
    local_only = set(("dictionary", "_memory", "attribute_locations",
                      "attribute_byte_offset", "struct", "create_struct",
                      "pack"))
                  
    def __init__(self, dictionary=None, memory_size=8192):
        self._memory = mmap.mmap(-1, memory_size)
        self.dictionary = dictionary if dictionary else {}
        self.create_struct()        
    
    def pack(self, value):
        format_character = Struct.format_switch.get(type(value), "pyobject")
        if format_character is "pyobject":
            value = pickle.dumps(value)
            format_size = len(value)
            format_character = str(format_size) + 'c'            
        else:
            format_size = Struct.format_size[format_character]
            if not format_size:
                format_size = len(value)
                format_character = str(format_size) + format_character
    
        return format_size, format_character, value
        
    def create_struct(self):        
        struct_layout = ''
        
        attribute_locations = self.attribute_locations = {}
        attribute_byte_offset = self.attribute_byte_offset = {}
        
        index_count = 0
        byte_index = 0
        values = []
        for key, value in self.dictionary.items():
            attribute_locations[key] = index_count
            format_size, format_character, value = self.pack(value)
            
            attribute_byte_offset[key] = slice(byte_index, byte_index + format_size)
            
            index_count += 1            
            struct_layout += format_character
            byte_index += format_size
            values.append(value)
                
        _struct = self.struct = struct.Struct(struct_layout)
        print "creating", values, struct_layout
        self._memory[:_struct.size] = _struct.pack(*values)   
        
    def __getattribute__(self, attribute):
        get_attribute = _get_attribute
        if "__" != attribute[:2] and attribute not in Struct.local_only:
            memory = get_attribute(self, "_memory")
            _struct = get_attribute(self, "struct")
            data_index = get_attribute(self, "attribute_locations")[attribute]
    #        print "retrieving {} at data index {}".format(attribute, data_index)
     #       print "values: ", _struct.unpack(memory[:_struct.size])
            value = _struct.unpack(memory[:_struct.size])[data_index]
        else:
      #      print "getting regular attribute {}".format(attribute)
            value = get_attribute(self, attribute)
        return value
        
    def __setattr__(self, attribute, value):
        get_attribute = _get_attribute
        
        if "__" != attribute[:2] and attribute not in Struct.local_only:
            dictionary = get_attribute(self, "dictionary")
            dictionary[attribute] = value
            get_attribute(self, "create_struct")()
            """memory = get_attribute(self, "_memory")
            data_slice = get_attribute(self, "attribute_byte_offset")[attribute]

            size, format, packed_data = get_attribute(self, "pack")(value)
            
            print memory[:32]
            print "setting {} {} to {} ({} bytes)".format(data_slice, 
                                                          [ord(char) for char in memory[data_slice]],
                                                          [ord(char) for char in reversed(packed_data)],
                                                          size)
                                         
            memory[data_slice] = ''.join(reversed(packed_data))
            print memory[:32]"""
        else:
            _set_attribute(self, attribute, value)
            
            
class Storage(object):
    
    def __init__(self, pyobject):
        memory = mmap.mmap(-1, 8192)
        version = '0' * 16
        memory.write(version)
        pickle.dump(pyobject, memory)  
        _set_attribute(self, "memory", memory)        
        _set_attribute(self, "pyobject", pyobject)
        _set_attribute(self, "version", version)
                
    def __getattribute__(self, attribute):
        get_attribute = _get_attribute
        memory = get_attribute(self, "memory")
        version = memory[:16]
        if version == get_attribute(self, "version"):
            pyobject = get_attribute(self, "pyobject")
        else:
            memory.seek(16)
            pyobject = pickle.load(memory)
            _set_attribute(self, "version", version)
            _set_attribute(self, "pyobject", pyobject)
        return getattr(pyobject, attribute)
            
    def __setattr__(self, attribute, value):
        memory = _get_attribute(self, "memory")
        
        memory.seek(0)
        version = memory.read(16)
        pyobject = pickle.load(memory)
        setattr(pyobject, attribute, value)
        
        memory.seek(0)
        new_version = str(int(version) + 1).zfill(16)
        _set_attribute(self, "version_number", new_version)
        memory.write(new_version)        
        pickle.dump(pyobject, memory)
        
        
if __name__ == "__main__":
    struc = Struct({"integer" : 123, 
                    "string" : "hi, i'm a string",
                    "float" : 1.0,
                    "boolean" : True,
                    "none" : None})
                    
                    
    def test():
        for x in xrange(10000):
            struc.integer
    from mpre.misc.decoratorlibrary import Timed
    from mpre.base import Base
    
    time = Timed(test)()
    print "10000 accesses took: ", time
    print "time per access: ", time / 10000
    base = Base(integer=123)
    storage = Storage(base)
    def test2():
        for x in xrange(10000):
            storage.integer
                        
    time2 = Timed(test2)()
    print "10000 pickle accesses took: ", time2
    print "time per access: ", time2 / 10000
    
    def test3():
        for x in xrange(10000):
            base.integer
    
    time3 = Timed(test3)()
    print "10000 regular accesses took: ", time3
    print "time per access: ", time3 / 10000
    
 
    print "unpacked: ", struc.struct.unpack(struc._memory[:struc.struct.size])
    print "struc.integer before: ", struc.integer
    struc.integer = 123456
    
    print "unpacked again: ", struc.struct.unpack(struc._memory[:struc.struct.size])
    print "struc.integer : ", struc.integer