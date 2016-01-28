import collections
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
                                                     
def get_structure_bytestream(structure):
    format_string = ''
    fields_format = []
    values = []
    _values = [] # do nested structs in a second pass afterwards
    for attribute, _type in structure._fields_:
        if _type == ctypes.c_char_p:
            character = str(len(getattr(structure, attribute))) + 's'
        else:
            try:
                character = format_character[_type]
            except KeyError:
                if issubclass(_type, ctypes.Structure):
                    _values.append((attribute, _type))
                    continue
                else:
                    raise
        format_string += character
        fields_format.append((attribute, character))
        value = getattr(structure, attribute)
        if value is None:
            value = 0
        values.append(value)  
    
    # this is a potentially more readable form of the code that follows
    #packed_data = utilities.pack_data(format_string) + struct.pack(format_string, *values)
    #for attribute, _type in _values:
    #    packed_data += get_structure_bytestream(getattr(structure, attribute))
    #return packed_data

    name = "{}_{}".format(type(structure).__name__, len(structure._fields_))
    print "Packing values: ", ([name, fields_format, struct.pack(format_string, *values)] + 
                               [get_structure_bytestream(getattr(structure, attribute)) for 
                                attribute, _type in _values])
    return utilities.pack_data(*[name, fields_format, struct.pack(format_string, *values)] + 
                                [(attribute, get_structure_bytestream(getattr(structure, attribute))) for 
                                 attribute, _type in _values])
        
def get_fields_format(structure):
    fields = []
    for name, _type in structure._fields_:
        if _type == ctypes.c_char_p:
            #_string = getattr(structure, name)
            character = str(len(getattr(structure, name))) + 's'
        else:
            try:
                character = format_character[_type]
            except KeyError:
                if issubclass(_type, ctypes.Structure):
                    character = "S"
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
    #name = structure.__class__.__name__
    #fields = [(name, character) for name, character in get_fields_format(structure)]
    #packed_bytes = get_structure_bytestream(structure)
    #return utilities.pack_data(name, fields, packed_bytes)
    return get_structure_bytestream(structure)
                               
def unpack_structure(packed_data):
    name, fields, packed_bytes = utilities.unpack_data(packed_data, 3)
    print "\nUnpacking structure"
    print "Name: ", name
    print "Fields: ", fields
    print "Packed data: ", packed_bytes
    fields = ast.literal_eval(fields)
    format_characters = ''.join(_type for name, _type in fields)
    print "Extracting c types from format characters: ", format_characters
    c_types = get_ctypes_from_format(format_characters)
    print "Got c types: ", c_types
    fields = [(field_info[0], c_types[index]) for index, field_info in enumerate(fields)]
    print "Unpacking fields: ", format_characters, len(packed_bytes), packed_bytes
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
    
def serialize(python_object):
    try:
        attributes = python_object.__reduce__()
    except (TypeError, AttributeError):
        if not isinstance(python_object, dict):
            attributes = python_object.__dict__
        else:
            attributes = python_object
    attribute_types = dict((key, type(value)) for key, value in attributes.items())
    struct_type = new_struct_type(python_object.__class__.__name__, **attribute_types)
    struct = struct_type(**attributes)
    return pack_structure(struct)
    
def deserialize(stream):
    struct = unpack_structure(stream)
    print type(struct).__name__, struct, dir(struct)
    return struct
    
def test_serialize_deserialize():
    data = {"int" : 1, "bool" : True, "float" : 0.0, "str" : "str", "None" : None}
    stream = serialize(data)
    _data = deserialize(stream)
    
        
class Persistent_Object(pride.base.Base):
    
    store_in_dict = ("memory", "size", "defaults", "flags", "mutable_defaults", "verbosity",
                     "startup_components", "required_attributes", "alert", "reference",
                     "store_in_dict", "objects", "struct_size", "references_to", "parent_name",
                     "references_to")    
        
    def __setattr__(self, attribute, value):
        print "Setting attribute: ", attribute, value
        if attribute[:2] == "__" or attribute in self.store_in_dict:
            super(Persistent_Object, self).__setattr__(attribute, value)
        else:
            print "Storing on disk: ", attribute
            try:
                packed_struct = self.memory[:self.struct_size]
            except AttributeError:
                reference = value if attribute == "reference" else self.reference
                with open(reference.replace("->", '_'), 'a+b') as _file:
                    self.memory = mmap.mmap(_file.fileno(), 65535)
                structure = new_struct_type(self.reference)()
            else:
                structure = unpack_structure(packed_struct)
            if attribute not in (name for name, _type in structure._fields_):
    #            print "Setting new attribute: ", attribute, value
                try:
                    struct_type = new_struct_type_from_ctypes(self.reference, 
                                                              *structure._fields_ + 
                                                              [(attribute, type_conversion[type(value)])])
                except KeyError:
                    try:
                        iterator = iter(value)
                    except TypeError:
                        # save an object
                        _struct_type = new_struct_type(value.__module__ + type(value).__name__,
                                                       *[(key, _value) for key, _value in
                                                          value.__dict__.items()])
                    else:
                        try:
                            iterator = iter(value.items())
                        except AttributeError:
                            # save a tuple/list/set
                            if isinstance(value, tuple):
                                name = "Tuple{}".format(len(value))
                            elif isinstance(value, list):
                                name = "List{}".format(len(value))
                            elif isinstance(value, set):
                                name = "Set{}".format(len(value))
                            else:
                                raise TypeError("Unable to serialize iterable of type '{}'".format(type(value)))
                            _struct_type = new_struct_type(name, *[(str(index), type(_value)) for index, _value in
                                                                   enumerate(value)])
                        else:
                            # save a dictionary
                            if not isinstance(value, dict):
                                raise Type_Error("Unable to serialize mapping of type '{}'".format(type(value)))
                            _struct_type = new_struct_type("Dict{}".format(len(value)), 
                                                           *[(key, _value) for key, _value in iterator])
                    struct_type = new_struct_type_from_ctypes(self.reference, 
                                                              *structure._fields_ + [(attribute, _struct_type)])
                _fields = struct_type._fields_
                #print "Instantiating structure: ", [(name, getattr(structure, name)) for name, _type in _fields[:-1]] + [value]
                structure = struct_type(*[getattr(structure, name) for name, _type in _fields[:-1]] + [value])
                #print "Made new structure", structure
            else:
    #            print "Set field attribute: ", attribute, value
                setattr(structure, attribute, value)
    #        print "packing and saving new structure... ", attribute, dir(structure)
            repacked_struct = pack_structure(structure)
            size = self.struct_size = len(repacked_struct)
            self.memory[:size] = repacked_struct
        
    def __getattribute__(self, attribute):
        print "Getting: ", attribute
        get_attribute = super(Persistent_Object, self).__getattribute__
        try:
        #if attribute[:2] == "__" or attribute in get_attribute("store_in_dict"):
            return get_attribute(attribute)
        except AttributeError:
            #memory = get_attribute("memory")
            #size = get_attribute("struct_size")
            #packed_structure = memory[:size]
            #structure = unpack_structure(packed_structure)
            #return getattr(structure, attribute)
            return getattr(unpack_structure(get_attribute("memory")[:get_attribute("struct_size")]), 
                           attribute)      
    
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
    
def test_pack_structure():
    test_fields = collections.OrderedDict()
    for test_type in (int, float, str, bool):
        test_fields["test_{}".format(test_type.__name__)] = test_type
  #  print test_fields.items()        
    struct_type = new_struct_type("Test_Structure", *test_fields.items())
    
    attributes = {"test_int" : 128, "test_float" : 10000.0,
                  "test_str" : "This is an *awesome* test string.",
                  "test_bool" : True}#, "test_NoneType" : None}
    test_attributes = collections.OrderedDict()
    field_names = test_fields.keys()
    for name in field_names:
        test_attributes[name] = attributes[name]
    
   # print [attributes[field_name] for field_name in field_names]
    
    structure = struct_type(*(attributes[field_name] for field_name in field_names))
    saved_structure = pack_structure(structure)
    print "Saved structure: "#, saved_structure
    print utilities.unpack_data(saved_structure, 3)
    loaded_structure = unpack_structure(saved_structure)
    for name, value in attributes.items():
        assert getattr(loaded_structure, name) == value
            
def test_Persistent_Object():
    persistent_object = Persistent_Object()
    for attribute, value in {"test_string" : "test!", "test_int" : 1,
                             "test_float" : 1000.0, "test_bool" : True,
                             "test_none" : None, "test_tuple" : (1, 'test', None)}.items():
        print "Setting: ", attribute, value
        setattr(persistent_object, attribute, value)
        print "Testing: ", attribute
        assert getattr(persistent_object, attribute) == value

if __name__ == "__main__":
    test_new_struct()
    print "\n\nPassed new struct test\n\n"
    test_pack_structure()  
    print "\n\nPassed pack_structure test\n\n"
    test_serialize_deserialize()
    print "\n\nPassed serialize/deserialize test\n\n"
    #test_Persistent_Object()  
    #print "\n\nPassed Persistent_Object test\n\n"