storage = {}
stores_in = {'LOAD_GLOBAL' : 'co_names',
             "IMPORT_FROM" : 'co_names',
             "IMPORT_NAME" : "co_names",
             "DELETE_NAME" : "co_names",
             "STORE_NAME" : "co_names",
             "LOAD_ATTR" : "co_names",
             'STORE_ATTR' : "co_names",
             'DELETE_ATTR' : "co_names",
             "LOAD_NAME" : "co_names",
             'LOAD_CONST' : 'co_consts',
             'LOAD_FAST' : 'co_varnames',
             'STORE_FAST' : "co_varnames",
             "DELETE_FAST" : "co_varnames",
             "LOAD_CLOSURE" : 'co_freevars co_cellvars',
             "COMPARE_OP" : "cmp_op",
             "JUMP_FORWARD" : 'bytecode_counter',
             "JUMP_ABSOLUTE" : 'bytecode_counter',
             'POP_BLOCK' : 'block_stack',
             'SETUP_LOOP' : "block_stack",
             "SETUP_EXCEPT" : "block_stack",
             "SETUP_FINALLY" : "block_stack",
             "EXTENDED_ARG" : "opcode",
             'STORE_MAP' : "dictionary",
             "STORE_GLOBAL" : '_global',
             'DELETE_GLOBAL' : '_global',
             "ADDRESS" : "continue_loop"}

BYTECODE_COUNTER = ["JUMP_FORWARD", 'JUMP_ABSOLUTE']

CMP_OP = ['COMPARE_OP']

BLOCK_STACK = ['POP_BLOCK', 'SETUP_LOOP', 'SETUP_EXCEPT', 'SETUP_FINALLY']

OPCODE = ['EXTENDED_ARG']

DICTIONARY = ['STORE_MAP']

GLOBAL = ['STORE_GLOBAL', 'DELETE_GLOBAL']

ADDRESS = ["CONTINUE_LOOP"]

# PRINT_ITEM_TO uses second to top of stack
TOS = ["POP_TOP", "ROT_TWO", 'ROT_THREE', 'ROT_FOUR', 'DUP_TUP',
       'UNARY_POSITIVE', 'UNARY_NEGATIVE', 'UNARY_NOT', 'UNARY_CONVERT',
       'UNARY_INVERT', 'GET_ITER', 'SLICE+0', "DELETE_SLICE+0",
       'PRINT_EXPR', 'PRINT_ITEM', 'PRINT_ITEM_TO', 'PRINT_NEWLINE_TO',
       "LIST_APPEND", "LOAD_LOCALS", "RETURN_VALUE", "YIELD_VALUE",
       'IMPORT_STAR', 'SETUP_WITH', 'STORE_NAME', 'UNPACK_SEQUENCE',
       'LOAD_CONST', 'LOAD_NAME', 'BUILD_TUPLE', 'BUILD_LIST', 'BUILD_MAP',
       'LOAD_ATTR', 'LOAD_GLOBAL', 'LOAD_FAST', 'STORE_FAST', 'LOAD_CLOSURE',
       'LOAD_DEREF', 'STORE_DEREF', 'CALL_FUNCTION', 'MAKE_FUNCTION',
       'CALL_FUNCTION_VAR', 'CALL_FUNCTION_KW', 'CALL_FUNCTION_VAR_KW',
       "FOR_ITER"]

TOS_TOS1 = ['BINARY_POWER', 'BINARY_MULTIPLY', 'BINARY_DIVIDE',
            'BINARY_FLOOR_DIVIDE', 'BINARY_TRUE_DIVIDE', 'BINARY_MODULO',
            'BINARY_ADD', 'BINARY_SUBTRACT', 'BINARY_SUBSCR',
            'BINARY_LSHIFT', 'BINARY_RSHIFT', 'BINARY_AND', 'BINARY_XOR',
            'BINARY_OR', "SLICE+1", "SLICE+2", 'STORE_SLICE+0',
            'DELETE_SLICE+1', 'DELETE_SLICE+2', 'STORE_ATTR', 'DELETE_ATTR',
            'IMPORT_NAME', 'POP_JUMP_IF_TRUE', 'POP_JUMP_IF_FALSE',
            'JUMP_IF_TRUE_OR_POP', 'JUMP_IF_FALSE_OR_POP', 'MAKE_CLOSURE',
            'BUILD_SLICE','INPLACE_POWER', 'INPLACE_MULTIPLY', 'INPLACE_DIVIDE',
            'INPLACE_FLOOR_DIVIDE', 'INPLACE_TRUE_DIVIDE', 'INPLACE_MODULO',
            'INPLACE_ADD', 'INPLACE_SUBTRACT', 'INPLACE_LSHIFT', 'INPLACE_RSHIFT',
            'INPLACE_AND', 'INPLACE_XOR', 'INPLACE_OR']

TOS_TOS2 = ["SLICE+3", 'STORE_SLICE+1', 'STORE_SLICE+2', 'DELETE_SLICE+3',
            'STORE_SUBSCR', 'DELETE_SUBSCR', 'EXEC_STMT', 'BUILD_CLASS',
            "WITH_CLEANUP", 'RAISE_VARARGS', 'BUILD_SLICE']

TOS_TOS3 = ['STORE_SLICE+3']

stack_storage = {}
STACK = [('TOS', TOS), ('TOS_TOS1', TOS_TOS1),
         ('TOS_TOS2', TOS_TOS2), ('TOS_TOS3', TOS_TOS3)]
for stack_size, stack_users in STACK:
    for user in stack_users:
        stack_storage[user] = stack_size

_range3 = range(0, 4)
SLICE = ["SLICE+{}".format(count) for count in _range3]
STORE_SLICE = ["STORE_{}".format(slice) for slice in SLICE]
DELETE_SLICE = ["DELETE_{}".format(slice) for slice in SLICE]
