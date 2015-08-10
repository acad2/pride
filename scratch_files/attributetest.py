import mmap
import struct
import ast
import cPickle as pickle
from itertools import izip

import mpre.base as base
import mpre.fileio as fileio


class Struct(object):
   
    format_switch = {int : 'q',
                     float : 'd',
                     str : 's',
                     bool : '?'}
    
    format_size = {'q' : 8,
                   'd' : 8,
                   's' : 0,
                   '?' : 1}
    
    local_only = set(("dictionary", "_memory", "unpacked_index",
                      "byte_offsets", "struct", "create_struct",
                      "pack", "metadata_struct", "struct_slice",
                      "total_size", "create_metadata", "from_dictionary",
                      "write_to_memory", "attribute_order", "is_pickled"))
                  
    def __init__(self, dictionary):
        self.update(dictionary)
    
    def update(self, dictionary):
        self.dictionary = dictionary
        self.data = self.byte_representation(dictionary)
        
    def byte_representation(self, dictionary):
        (total_size,
         packed_data,
         self.struct,
         self.struct_slice,
         self.unpacked_index,
         self.byte_offsets,
         self.attribute_order,
         self.is_pickled) = self.from_dictionary(dictionary)
        
        return packed_data
        
    def from_dictionary(self, dictionary):
        (byte_offsets,
         unpacked_index,
         attribute_order, 
         values, 
         _struct,
         is_pickled) = self.create_struct(dictionary)
                 
        """(packed_metadata, 
         metadata_struct) = self.create_metadata(attribute_order, 
                                                 byte_offsets,
                                                 is_pickled)
      
        metadata_size = len(packed_metadata)
        size_string = str(metadata_size).zfill(64)
        total_size = 64 + metadata_size + _struct.size
        
        struct_slice = slice(metadata_size + 64, total_size)       
         
        return (total_size, size_string, _struct.pack(*values),
                packed_metadata, _struct, metadata_struct, 
                struct_slice,  unpacked_index, byte_offsets,
                attribute_order, is_pickled)"""
        total_size = _struct.size
        struct_slice = slice(0, total_size)
        return (total_size, _struct.pack(*values),
                _struct, struct_slice,  unpacked_index, byte_offsets,
                attribute_order, is_pickled)
                
    def create_metadata(self, attribute_order, byte_offsets, is_pickled):
        """ create a metadata struct that provides attribute names,
            the pickled flag, and the associated offset/size."""
        metadata_layout = ''
        metadata_values = []
        for attribute in attribute_order:
            metadata_layout += str(len(attribute)) + 's?qq'
            start_pointer, end_pointer = byte_offsets[attribute]
            
            metadata_values.extend((attribute,
                                    is_pickled[attribute],
                                    start_pointer,
                                    end_pointer))
                                               
        metadata_struct = struct.Struct(metadata_layout)        
        packed_metadata = metadata_struct.pack(*metadata_values)
                
        return packed_metadata, metadata_struct
                                                       
    def pack(self, value):
        format_character = Struct.format_switch.get(type(value), "pyobject")
        if format_character is "pyobject":
        #    print "PICKLING: ", type(value), value
            value = pickle.dumps(value)
            format_size = len(value)
            format_character = str(format_size) + 's'  
            is_pickled = True
        else:
            format_size = Struct.format_size[format_character]
            if not format_size:
                format_size = len(value)
                format_character = str(format_size) + format_character
            is_pickled = False
            
       # print "packed {} into {}".format(value, format_character)
        return format_size, format_character, value, is_pickled
        
    def create_struct(self, dictionary):        
        struct_layout = ''
        
        unpacked_index = {}
        attribute_byte_offset = {}
        is_pickled = {}
        
        index_count = 0
        byte_index = 0
        attribute_order = []
        values = []
        for key, value in dictionary.items():
            attribute_order.append(key)
            unpacked_index[key] = index_count
            format_size, format_character, value, pickled_flag = self.pack(value)
            
            values.append(value)
            attribute_byte_offset[key] = byte_index, byte_index + format_size
          #  print '{} PICKLED flag: {}'.format(key, pickled_flag)
            is_pickled[key] = pickled_flag
            
            index_count += 1            
            struct_layout += format_character
            byte_index += format_size
                                           
        return (attribute_byte_offset, unpacked_index,
                attribute_order, values, struct.Struct(struct_layout),
                is_pickled)
        
        
class Persistent_Reactor(base.Base):
    
    local_only = set(('_file', '_memory', "_struct", "dictionary",
                      "instance_number", "instance_name", "environment",
                      "local_only", "defaults"))
    
    def __init__(self, **kwargs):
        print Persistent_Reactor, "__init__"
        super_object = super(Persistent_Reactor, self)
        set_attribute = super_object.__setattr__
                
        dictionary = {}
        fileio.ensure_file_exists(self.instance_name)
        _file = self._file = open(self.instance_name, 'r+b')
        memory = self._memory = mmap.mmap(_file.fileno(), 65535)
        
        _struct = Struct(dictionary)
        print "setting _struct and dictionary attributes"
        set_attribute("_struct", _struct)
        set_attribute("dictionary", dictionary)
        print self, "pre super"
        super_object.__init__(**kwargs)
        print self, "post super"
     

        packed_attributes = _struct.data
        memory[len(packed_attributes)] = packed_attributes
        
    def __getstate__(self):
        dict_copy = self.__dict__.copy()
        for attribute in self.local_only:
            if attribute in dict_copy:
                del dict_copy[attribute]
                
    #    del dict_copy["_file"]
     #   del dict_copy["_memory"]
      #  del dict_copy["_struct"
        return dict_copy
        
    def __setstate__(self, state):
        self.__init__(**state)
        
    def __getattribute__(self, attribute):
        get_attribute = super(Persistent_Reactor, self).__getattribute__
        try:
            value = get_attribute(attribute)
        except AttributeError:
            pass
            
        if "__" != attribute[:2] and attribute not in get_attribute("local_only"):
            print "getting shared attribute: ", attribute
            _struct = get_attribute("_struct")
            data_index = _struct.unpacked_index[attribute]
            value = _struct.struct.unpack(get_attribute("_memory")\
                                         [_struct.struct_slice])[data_index]
        else:
            value = get_attribute(attribute)
        return value
        
    def __setattr__(self, attribute, value):
      #  print "Setting {} to {}".format(attribute, value)
        get_attribute = super(Persistent_Reactor, self).__getattribute__
        if attribute not in get_attribute("local_only"):
       #     print "{} is a persistent attribute".format(attribute)
            _struct = get_attribute("_struct")
            
            _struct.update(self.dictionary)
            packed_dictionary = _struct.data
            get_attribute("_memory")[:len(packed_dictionary)] = packed_dictionary            
        else:
            super(Persistent_Reactor, self).__setattr__(attribute, value)       
            
                
if __name__ == "__main__":
    import unittest
    import mpre.misc.decoratorlibrary
    import mpre.base
    Base = mpre.base.Base
    Timed = mpre.misc.decoratorlibrary.Timed
    
    b = Base(none=None)
    struc_attributes = {"integer" : 123, 
                        "string" : "hi, i'm a string",
                        "float" : 1.0,
                        "boolean" : True,
                        "none" : None}
        
    struc = Struct(struc_attributes)    
    
    """print '{:+>80}'.format('TIMING COMPARISON')
    print "struct getattr: ", Timed(lambda: struc.none, iterations=10000)()
    print "base getattr  :  ", Timed(lambda: b.none, iterations=10000)()
    print
    print "struct setattr: ", Timed(lambda: struc.none, iterations=10000)()
    print "base setattr  : ", Timed(lambda: b.none, iterations=10000)()    
    print "write_to_memory time: ", Timed(lambda: struc.write_to_memory(struc.dictionary), iterations=10000)()
    print '{:+>80}'.format('END TIMING COMPARISON')"""

    
    class Test_getsetattr(unittest.TestCase):
  
        def test(self):
            index = 0
            print "\nTesting getattr and setattr accuracy"
            modifications = (Base(), None, "a shared memory string!", False, 123)
            
            for attribute, value in struc_attributes.items():
                attr_value = getattr(struc, attribute)
                print "\n\ntesting initially assigned attribute {} {} is {}".format(attribute, attr_value, value)
                self.failUnless(attr_value == value)
                
                modification = modifications[index]
                print "Modifying {}; changing {} to {}".format(attribute, 
                                                               attr_value,
                                                               modification)
                                                               
                setattr(struc, attribute, modification)
                test = getattr(struc, attribute)
                
                print "...testing modification {} is {}".format(test, modification)   
                
                if struc.is_pickled[attribute]:
                    test = type(test)
                    modification = type(modification)

                self.failUnless(test == modification)
                index += 1
    
    unittest.main()