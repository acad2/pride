import mmap
import ast
import struct
import ctypes

import pride.base
import utilities

type_conversion = {int : ctypes.c_longlong, float : ctypes.c_double,
                   bool : ctypes.c_bool, str : ctypes.c_char_p, 
                   unicode : ctypes.c_wchar_p, type(None) : ctypes.c_void_p}

c_to_python = dict((value, key) for key, value in type_conversion.items())
                   
format_character = {ctypes.c_longlong : 'q', ctypes.c_longdouble : 'd',
                    ctypes.c_bool : '?', ctypes.c_void_p : 'l',
                    ctypes.c_double : 'd'}
             
format_to_type = dict((value, key) for key, value in format_character.items())
             
def new_struct_type(struct_name, *_fields, **fields):
    print "Making new struct with fields: ", _fields, fields.items()
    if not (_fields or fields):
        return type(struct_name, (ctypes.Structure, ), {"_fields_" : []})
    else:
        return type(struct_name, (ctypes.Structure, ), 
                    {"_fields_" : [(attribute, type_conversion[value]) for
                                    attribute, value in _fields or fields.items()]})
                                
def new_struct_type_from_ctypes(struct_name, *_fields, **fields):
    if not (_fields or fields):
        return type(struct_name, (ctypes.Structure, ), {"_fields_" : []})
    else:
        return type(struct_name, (ctypes.Structure, ), 
                    {"_fields_" : [(attribute, value) for
                                    attribute, value in _fields or fields.items()]})                                
                                    
def test_new_struct():                
    struct_type = new_struct_type("test_structure", test_int=int, test_float=float,
                                  test_None=type(None), test_bool=bool, test_str=str, 
                                  test_unicode=unicode)
    structure = struct_type(test_int=1, test_float=10.0, test_None=None, test_bool=True, 
                         test_str="Test_string!", test_unicode="Test_unicode!")
    assert structure.test_int == 1, structure.test_int
    assert structure.test_float == 10.0, structure.test_float
    assert structure.test_None == None, structure.test_None
    assert structure.test_bool == True, structure.test_bool
    assert structure.test_str == "Test_string!"
    assert structure.test_unicode == "Test_unicode!"
    
def get_structure_bytestream(structure):
    return structure.__reduce__()[1][1][1]
    
def pack_structure(structure):
    name = structure.__class__.__name__
    fields = []
    for name, _type in structure._fields_:
        if _type == ctypes.c_char_p:
            f
    fields = str([(name, format_character[_type]) for name, _type in structure._fields_])
    packed_bytes = get_structure_bytestream(structure)
    return utilities.pack_data(name, fields, packed_bytes)
                            
def unpack_structure(packed_data):
    name, fields, packed_bytes = utilities.unpack_data(packed_data, 3)
    fields = ast.literal_eval(fields)
    format_characters = ''.join(_type for name, _type in fields)
    fields = [(name, format_to_type[character]) for name, character in fields]
    values = struct.unpack(format_characters, packed_bytes)
    struct_type = new_struct_type_from_ctypes(name, *fields)
    return struct_type(*values)
    
def test_pack_unpack():    
    struct_type = new_struct_type("Test_Structure", test_int=int, test_float=float)
    structure = struct_type(test_int=128, test_float=10000.0)
    packed_struct = get_structure_bytestream(structure)    
    fields = struct_type._fields_
    _struct = unpack_structure("Test_Structure", fields, 
                               ''.join(format_character[_type] for name, _type in fields),
                               packed_struct)
    assert _struct.test_int == 128
    assert _struct.test_float == 10000.0
   
#test_pack_unpack()    

def test_pack_structure():
    struct_type = new_struct_type("Test_Structure", test_int=int, test_float=float)
    structure = struct_type(test_int=128, test_float=10000.0)
    saved_structure = pack_structure(structure)
    loaded_structure = unpack_structure(saved_structure)
    assert loaded_structure.test_int == 128
    assert loaded_structure.test_float == 10000.0
    
test_pack_structure()
    
class Persistent_Object(pride.base.Base):
    
    store_in_dict = ("memory", "size", "defaults", "flags", "mutable_defaults", "verbosity",
                     "startup_components", "required_attributes", "alert", "instance_name",
                     "store_in_dict", "objects", "struct_size")
    
    def __init__(self, **kwargs):
        super(Persistent_Object, self).__init__(**kwargs)
                
        
    def __setattr__(self, attribute, value):
        if attribute[:2] == "__" or attribute in self.store_in_dict:
            print "Setting attribute: ", attribute, value
            super(Persistent_Object, self).__setattr__(attribute, value)
        else:
            try:
                packed_struct = self.memory[:self.struct_size]
            except AttributeError:
                with open(self.instance_name.replace("->", '_'), 'a+b') as _file:
                    self.memory = mmap.mmap(_file.fileno(), 65535)
                structure = new_struct_type(self.instance_name)()
            else:
                structure = unpack_structure(packed_struct)
            if attribute not in (name for name, _type in structure._fields_):
                print "Setting new attribute: ", attribute, value
                struct_type = new_struct_type_from_ctypes(self.instance_name, 
                                                          *structure._fields_ + 
                                                           [(attribute, type_conversion[type(value)])])
                _fields = struct_type._fields_
                print "Instantiating structure: ", [(attribute, getattr(structure, attribute)) for attribute, _type in _fields[:-1]] + [value]
                structure = struct_type(*[getattr(structure, attribute) for attribute, _type in _fields[:-1]] + [value])
                print "Made new structure"
            else:
                print "Set field attribute: ", attribute, value
                setattr(structure, attribute, value)
            repacked_struct = pack_structure(structure)
            size = self.struct_size = len(repacked_struct)
            self.memory[:size] = repacked_struct
        
    def __getattribute__(self, attribute):
        print "Getting: ", attribute
        get_attribute = super(Persistent_Object, self).__getattribute__
        if attribute[:2] == "__" or attribute in get_attribute("store_in_dict"):
            return get_attribute(attribute)
        else:
            #memory = get_attribute("memory")
            #size = get_attribute("struct_size")
            #packed_structure = memory[:size]
            #structure = unpack_structure(packed_structure)
            #return getattr(structure, attribute)
            return getattr(unpack_structure(get_attribute("memory")[:get_attribute("size")]), 
                           attribute)      
    
def test_Persistent_Object():
    persistent_object = Persistent_Object()
    persistent_object.test_attribute = "test!"
    
test_Persistent_Object()    