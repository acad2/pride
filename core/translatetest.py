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


source = """
a = "testing"
def testing(argument):
    def sub_test():
        b = a
        x = 10
        y = object()
        return argument

    if argument:
        print "This is more complex", argument
    return sub_test()
testing()"""



code = compile(source, 'exec', 'exec')
def testing(a, z):
    if z:
        if a:
            x = 10
            while x:
                x -= 1
    else:
        y = map
        y(lambda arg: arg, [z, a])
code = testing.func_code

from base import Base
code = Base.create.function.func_code

dis.dis(code)
print "co_code 82:", ord(code.co_code[82]), len(code.co_code)
bytecode = Bytecode(code)


print bytecode.jump_table
#bytecode.display(co_vars=False)

#bytecode.create_paths()

#print translator(source)
