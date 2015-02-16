import ast
import sys
import dis
import ast
from collections import OrderedDict

import bytecodemap

symbol_translator = {"*" : "__mul__",
                     "/" : "__div__",
                     "+" : "__add__",
                     "-" : "__sub__"}

block_stack = [0 for x in xrange(256)]
cmp_op = dis.cmp_op
bytecode_counter = []
opcode = []
dictionary = {}
_global = []
continue_loop = []
TOS = []
TOS_TOS1 = []
TOS_TOS2 = []
TOS_TOS3 = []
def translator(statement):
    if "." in statement:
        # base.create("testing.Testing")
        _object, method_call = statement.split('.')
        method, arguments = method_call.split("(")
        arguments = "(" + arguments
    else:
        _object, method, arguments = statement.split()

    try:
        method = symbol_translator[method]
    except KeyError:
        pass
    call = getattr(ast.literal_eval(_object), method)
    return call(ast.literal_eval(arguments))


valid_bytecodes = [opcode for opcode in dis.opname if "<" and ">" not in opcode]


class Bytecode(object):

    def __init__(self, code=None, source=None):
        if source:
            code = compile(source, 'bytecode', 'exec')
        elif not code:
            print "No source or code supplied for Bytecode object"
            raise SystemExit
        self.code = code
        self.opcode_list = []
        self.code_blocks = []
        self.address_in = OrderedDict()
        self.block_jump_table = OrderedDict()
        self.jump_table = OrderedDict()
        self.jump_conditions = OrderedDict()
        self.block_addresses = OrderedDict()
        self.block_ranges = []
        self.dump_opcodes()

    def display(self, co_vars=True):
        if co_vars:
            co_values = []
            for co_attr, value in self.dump_co_info():
                co_values.append((co_attr, value))
                print co_attr, value

        print

        for address, block in self.block_addresses.items():
            print"Block {0: ^}".format(address)
            for opcode in block:
                print "{0: >15} {1: <20} {2: <2} ({3: <1})".format(*opcode)

    def dump_co_info(self):
        return ((item, getattr(self.code, item)) for item in dir(self.code) if 'co' == item[:2])

    def get_block_info(self):
        block_jump_table = self.block_jump_table
        block_ranges = self.block_ranges
        code_blocks = self.code_blocks
        jump_targets = []

        for block_number, block in enumerate(code_blocks):
            first_address, _, _, _ = block[0]
            last_address, _, _, jump_target = block[-1]
            block_ranges.append(range(first_address, last_address))
            jump_targets.append((block_number, jump_target))

          #  print "block #{0}: {1} jumps to target {2}".format(block_number, (first_address, last_address), jump_target)



        for block_number, jump_target in jump_targets:
            #print "checking block number", block_number
            for next_block, block_range in enumerate(block_ranges):
                if jump_target in block_range:
                    block_jump_table[block_number] = next_block
                    break
            #else:
                #print "block jump from block {1} to address {0} was not in any range".format(jump_target, block_number)
                #for no, _range in enumerate(block_ranges):
                 #   print no, _range
                #raise SystemExit
        return block_ranges, block_jump_table

    def create_paths(self):
        block_jump_table = self.block_jump_table
        code_blocks = self.code_blocks
        paths = self.paths = {}
        print
        for block_number, block in enumerate(code_blocks):
            index = block_jump_table[block_number]
           # print "block {0} jumps to block {1}".format(block_number, index)
            next_block = code_blocks[index]
            paths[block_number] = (block, next_block)

        return paths
        """jump_conditions = self.jump_conditions
        jump_table = self.jump_table

        opcode_list = self.opcode_list
        block_addresses = self.block_addresses
        addresses = block_addresses.keys()
        blocks = block_addresses.values()

        for jump_from, jump_to in jump_table.items():
            conditional, on_condition = jump_conditions[jump_from]

            if conditional is "forward":
                pass
            else:
                print "Jump from {0} to {1} if {2} is {3}".format(jump_from, jump_to, conditional, on_condition)"""


    def get_jump_conditionss(self):
        opcodes, block_list = self.dump_opcodes()
        route_number = 0
        route = {}
        branches_at = {}
        jump_conditions = self.jump_conditions

        for block in block_list:
            for address, opcode, arg_location, arg_name in block:
                if "JUMP" in opcode:
                    jump_from = conditional_address

                    if opcode == 'POP_JUMP_IF_FALSE':
                        jump_conditions[address] = (conditional, False)

                    elif opcode == "POP_JUMP_IF_TRUE":
                        jump_conditions[address] = (conditional, True)

                    elif opcode == "JUMP_ABSOLUTE":
                        jump_conditions[address] = ('absolute', 'absolute')

                    elif opcode == "JUMP_FORWARD":
                        jump_conditions[address] = ("forward", "forward")

                conditional = arg_name
                conditional_address = address
        return jump_conditions

    def dump_opcodes(self):
        """bytecode.dump_opcodes() => opcodes_list, block_list

        opcodes_list contains address, opcode, arg_address, arg tuples
        block_list contains block_address, block_code tuples"""
        code = self.code
        opcodes = code.co_code

        opcode_list = self.opcode_list
        jump_table = self.jump_table
        block_addresses = self.block_addresses
        code_blocks = self.code_blocks

        block_finished = False
        block_address = 0
        block = []
        block_addresses[0] = block

        argument = False
        for address, opcode in enumerate(opcodes):
            index = ord(opcode)

            if not argument:

                if index:
                    code_name = dis.opname[index]
                    operation_info = (address, code_name)
                    argument = index >= dis.HAVE_ARGUMENT
                    if "JUMP" in code_name:
                        jump_opcode = code_name
                        jump_address = address
                        block_finished = True
                        #elif code_name == "SETUP_EXCEPT":
                            #block_finished = False
                          #  block.append("consolidate")
                    if not argument:
                        operation_info += ('', '')
                        opcode_list.append(operation_info)
                        block.append(operation_info)

            else:
                argument = False
                arg_value = index + ord(opcodes[address+1]) * 256

                try:
                    location = bytecodemap.stores_in[code_name]
                except KeyError:
                    location = bytecodemap.stack_storage[code_name]

                try:
                    value = getattr(code, location)
                except AttributeError:
                    value = globals()[location]

                try:
                    _argument = value[index]
                except IndexError:
                    unhandled = "{0} argument {1} is unhandled".format(code_name, location)
                    #print unhandled
                    _argument = ''#(unhandled, value)
                operation_info += (index, _argument)
                block.append(operation_info)
                opcode_list.append(operation_info)
                if block_finished:

                    if jump_opcode == "JUMP_FORWARD":
                        _address, _code_name, _location, _arg = block.pop()
                        _argument = jump_address + index + 3
                        block.append((_address, _code_name, index, _argument))

                    else:
                        _address, _code_name, _location, _arg = block.pop()
                        _argument = _location
                        block.append((_address, _code_name, _location, _argument))

                    jump_table[jump_address] = _argument
                    block_finished = False
                    code_blocks.append(block)
                    block = []
                    block_addresses[address + 2] = block
        else:
            code_blocks.append(block)

        self.get_block_info()
        return opcode_list, code_blocks


def attribute_lookup(opcodes, index):
    position = 0
    variable_name = opcodes[index][3]
    names = [variable_name]
    searching = True
    
    while searching:
        position += 1
        new_code = opcodes[index - position]
        new_code_name = new_code[1]
        new_code_value = new_code[3]
        
        if new_code_name in ("LOAD_FAST", "LOAD_GLOBAL", "LOAD_ATTR"):
            if new_code_value == names[-1]:
                continue
            searching = False
            names.append(new_code_value)
         #   print "\t{} is an attribute of {}".format(variable_name, new_code[3])                                            
    return '.'.join(reversed(names))
    

def next_stored_variable(opcodes, index):
    position = 0
    searching = True
    while searching:
        position += 1
        next_code = opcodes[index + position]
        next_code_name = next_code[1]
        
        if next_code_name in ("STORE_FAST", "STORE_GLOBAL", "STORE_ATTR",
                              "RETURN_VALUE"):
            searching = False
            if next_code_name == "STORE_ATTR":
                value = attribute_lookup(opcodes, index + position)
            else:
                value = next_code[3]
    return value

    
def type_variables(bytecode):
    name_types = {}
    equalities = {}
    
    opcodes = bytecode.opcode_list
    for index, code in enumerate(opcodes):
        code_name = code[1]
        variable_name = code[3]
        
        top_of_stack = opcodes[index - 1]
        store_code = top_of_stack[1]
        store_value = top_of_stack[3]
            
        if code_name == "INPLACE_ADD":
            second_of_stack = opcodes[index - 2]
            second_code = second_of_stack[1]
            second_value = second_of_stack[3]
                        
            if second_code == 'LOAD_CONST':
                _type = type(second_value)
            elif store_code == "LOAD_CONST":
                _type= type(store_value)
            
            variable = next_stored_variable(opcodes, index)
            name_types[variable] = _type
            continue
                
        if code_name in ("STORE_FAST", "STORE_GLOBAL", "STORE_ATTR",
                         "RETURN_VALUE"):
              
            if code_name == "STORE_ATTR":
                full_name = attribute_lookup(opcodes, index)
                equalities[variable_name] = full_name
                continue
                
            if store_code == "LOAD_CONST":
                if code_name == "RETURN_VALUE":
                    return_value_info = (type, type(store_value))
                
                name_types[variable_name] = type(store_value)
                
            if store_code == "LOAD_FAST":
                print "LOAD_FAST setting equalities[{}] = {}".format(variable_name, store_value)
                 
                equalities[variable_name] = store_value
                
            if store_code == "LOAD_ATTR":
                full_name = attribute_lookup(opcodes, index)
                print "Loaded attribute: ", full_name
                equalities[variable_name] = full_name
                
                if code_name == 'RETURN_VALUE':
                    return_value_info = ("equality", full_name)
                    
    print "types: ", name_types
    print "equalities: ", equalities
    print "return value: ", return_value_info        
    return name_types, equalities, return_value_info
 
def type_names(_dict):
    return dict((key, type(value)) for key, value in _dict.items())
    
def simpletest():
    x = 1
    y = 1.0
    z = "test_string"
    boolean = True
    

def compile_source(method):
    bytecode = Bytecode(method.func_code)
    types, equalities, return_type = type_variables(bytecode)
    function_source = inspect.getsource(method)
    declarations = []
    declare = "cdef {} {}"
    
    type_map = {int : "int",
                float : "double",
                bool : "bint",
                str : "str"}
                
    for name, _type in types.items():
        declarations.append(declare.format(type_map[_type], name))
        
    start_of_def = function_source.index("def ")
    end_of_def = function_source.index("):")
    
    indent_level = function_source[:end_of_def].count("    ")
    if not indent_level:
        indent_level = function_source[:end_of_def].count("\t")
    
    indent = indent_level * "    "
    code_indent = "\n{}   ".format(indent)
    
    def_header = function_source[:end_of_def + 2]
    cdef_header = indent + 'c' + def_header[start_of_def:] + code_indent + " "
    
    partial_source = function_source[end_of_def + 2:]
    
    compilable_function = cdef_header + code_indent.join(declarations) + "\n" + partial_source
    
    compileable = compilable_function.replace("\t", '    ')    
    print compileable
    with open("testconvert.pyx", 'w') as cfile:
        cfile.write(compileable)
        cfile.flush()
        cfile.close()

        
if __name__ == "__main__":
    import inspect
    import mpre.base as base
    code = base.Base.__init__.func_code
    global_types = type_names(globals()) 

    print inspect.getsource(base.Base.__init__)
    bytecode = Bytecode(code)
    bytecode.display(co_vars=False)
    compile_source(base.Base.__init__)