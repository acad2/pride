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
                    ctypes.c_bool : '?', ctypes.c_void_p : 'L',
                    ctypes.c_double : 'd'}
             
format_to_type = dict((value, key) for key, value in format_character.items())
             
def new_struct_type(struct_name, *_fields, **fields):
#    print "Making new struct with fields: ", _fields, fields.items()
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
    format_string = ''.join(character for name, character in get_fields_format(structure))
    values = []
    for attribute, _type in structure._fields_:
        value = getattr(structure, attribute)
        if value is None:
            value = 0
        values.append(value)    
    return struct.pack(format_string, *values)
        
def get_fields_format(structure):
    fields = []
    for name, _type in structure._fields_:
        if _type == ctypes.c_char_p:
            #_string = getattr(structure, name)
            character = str(len(getattr(structure, name))) + 's'
        else:
            character = format_character[_type]
        yield (name, character)    
    
def get_ctypes_from_format(format_characters):
    c_types = []
    ignore_count = 0
    for index, character in enumerate(format_characters):
        if ignore_count:
            ignore_count -= 1
            continue           
  #      print "Getting type from format character: ", character
        try:
            c_types.append(format_to_type[character])
        except KeyError:
            number = ''
            offset = 0
            while True:
                try:                    
                    int(format_characters[index + offset])                        
                except ValueError:
                    break                               
                else:
                    number += character
                    offset += 1
            c_types.append(ctypes.c_char_p)
            ignore_count = offset
    return c_types
    
def pack_structure(structure):
    name = structure.__class__.__name__
    fields = [(name, character) for name, character in get_fields_format(structure)]
    #fields = str([(name, format_character[_type]) for name, _type in structure._fields_])
    packed_bytes = get_structure_bytestream(structure)
    #print "Packed bytes: ", fields, packed_bytes
    return utilities.pack_data(name, fields, packed_bytes)
                            
def unpack_structure(packed_data):
    name, fields, packed_bytes = utilities.unpack_data(packed_data, 3)
    fields = ast.literal_eval(fields)
   # print "Fields: ", fields
    format_characters = ''.join(_type for name, _type in fields)
  #  print "Extracting c types from format characters: ", format_characters
    c_types = get_ctypes_from_format(format_characters)
  #  print "Got c types: ", c_types
    fields = [(field_info[0], c_types[index]) for index, field_info in enumerate(fields)]
  #  print "Unpacking fields: ", format_characters, fields
    #fields = [(name, format_to_type[character]) for name, character in fields]
    values = struct.unpack(format_characters, packed_bytes)
    _values = []
    for value, _type in zip(values, (field[1] for field in fields)):
        if _type == ctypes.c_void_p:
            _values.append(None)
        else:
            _values.append(value)
    struct_type = new_struct_type_from_ctypes(name, *fields)
    return struct_type(*values)   
    
class Persistent_Object(pride.base.Base):
    
    store_in_dict = ("memory", "size", "defaults", "flags", "mutable_defaults", "verbosity",
                     "startup_components", "required_attributes", "alert", "instance_name",
                     "store_in_dict", "objects", "struct_size")
    
    def __init__(self, **kwargs):
        super(Persistent_Object, self).__init__(**kwargs)
                
        
    def __setattr__(self, attribute, value):
        if attribute[:2] == "__" or attribute in self.store_in_dict:
    #        print "Setting attribute: ", attribute, value
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
    #            print "Setting new attribute: ", attribute, value
                try:
                    struct_type = new_struct_type_from_ctypes(self.instance_name, 
                                                              *structure._fields_ + 
                                                              [(attribute, type_conversion[type(value)])])
                except KeyError:
                    try:
                        iterator = iter(value)
                    except TypeError:
                        # save an object
                        pass
                    else:
                        try:
                            
                    
                _fields = struct_type._fields_
    #            print "Instantiating structure: ", [(attribute, getattr(structure, attribute)) for attribute, _type in _fields[:-1]] + [value]
                structure = struct_type(*[getattr(structure, attribute) for attribute, _type in _fields[:-1]] + [value])
     #           print "Made new structure"
            else:
    #            print "Set field attribute: ", attribute, value
                setattr(structure, attribute, value)
            repacked_struct = pack_structure(structure)
            size = self.struct_size = len(repacked_struct)
            self.memory[:size] = repacked_struct
        
    def __getattribute__(self, attribute):
    #    print "Getting: ", attribute
        get_attribute = super(Persistent_Object, self).__getattribute__
        if attribute[:2] == "__" or attribute in get_attribute("store_in_dict"):
            return get_attribute(attribute)
        else:
            #memory = get_attribute("memory")
            #size = get_attribute("struct_size")
            #packed_structure = memory[:size]
            #structure = unpack_structure(packed_structure)
            #return getattr(structure, attribute)
            return getattr(unpack_structure(get_attribute("memory")[:get_attribute("struct_size")]), 
                           attribute)      
    
  
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
   # print "Saved structure: ", saved_structure
   # print utilities.unpack_data(saved_structure, 3)
    loaded_structure = unpack_structure(saved_structure)
    assert loaded_structure.test_int == 128
    assert loaded_structure.test_float == 10000.0
    
#test_pack_structure()  

def test_Persistent_Object():
    persistent_object = Persistent_Object()
    for attribute, value in {"test_string" : "test!", "test_int" : 1,
                             "test_float" : 1000.0, "test_bool" : True,
                             "test_none" : None, "test_tuple" : (1, 'test', None)}.items():
        setattr(persistent_object, attribute, value)
        assert getattr(persistent_object, attribute) == value
test_Persistent_Object()  