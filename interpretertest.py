import types
import inspect
import dis

import pride

X = 1
    
class Function(pride.base.Wrapper):
    
    wrapped_object_name = "function"
    
    @classmethod
    def wrap_function(cls, function):
        return cls(wrapped_object=function)
    
    def __init__(self, **kwargs):
        super(Function, self).__init__(**kwargs)
        arg_specification = inspect.getargspec(self.function)
        _locals = {}
        self._args = args = arg_specification.args
        self._varargs = varargs = arg_specification.varargs
        self._keywords = keywords = arg_specification.keywords
        defaults = self._defaults = arg_specification.defaults
        self._no_defaults = len(args) - len(defaults) if defaults else 0
        try:
            self._code = self.function.func_code
        except AttributeError:
            self._code = self.function.im_func.func_code
        
    def __call__(self, *args, **kwargs):
        _locals = {}#self._locals
        defaults = self._defaults
        no_defaults = self._no_defaults
        for index, arg_name in enumerate(self._args):
            if arg_name in kwargs:
                value = kwargs.pop(arg_name)
            else:
                try:
                    value = args[index]
                except IndexError:
                    value = defaults[index - no_defaults]
            _locals[arg_name] = value
        if self._varargs:
            _locals[self._varargs] = args[index + 1:]
        if self._keywords:
            _locals[self._keywords] = kwargs
        frame = Stack_Frame(_locals, self)
        return objects["->Bytecode_Interpreter"].execute_code(self._code, frame)
    
class Stack_Frame(object):
    
    def __init__(self, _locals, parent):
        self.locals = _locals
        self.parent = parent
        self.stack = []
        
        
class Bytecode_Interpreter(pride.base.Base):
            
    flags = {"_bytecode_counter" : None, "_delta" : 0}.items()
    
    def __init__(self, **kwargs):
        super(Bytecode_Interpreter, self).__init__(**kwargs)
        self._method_name = {"<" : "__lt__", "<=" : "__le__", ">" : "__gt__", ">=" : "__ge__",
                             "==" : "__eq__", "!=" : "__ne__", "in" : "__contains__"}
                             
        self.operation_handlers = dict((dis.opmap[name.upper()], getattr(self, name.replace('+', '_'))) for name in 
                                       ("pop_top", "rot_two", "rot_three", "rot_four", "dup_top",
                                        "unary_positive", "unary_negative", "unary_not", 
                                        "unary_convert", "unary_invert", "get_iter",
                                        "slice+0", "slice+1", "slice+2", "slice+3",
                                        "store_slice+0", "store_slice+1", "store_slice+2",
                                        "store_slice+3", "delete_slice+0", "delete_slice+1",
                                        "delete_slice+2", "delete_slice+3", "delete_subscr",
                                        "print_expr", "print_item_to", "print_newline_to",
                                        "break_loop", "continue_loop", "load_locals",
                                        "yield_value", "import_star", "exec_stmt", "pop_block",
                                        "end_finally", "setup_with", "with_cleanup", 
                                        "store_name", "delete_name", "unpack_sequence", "dup_topx",
                                        "store_attr", "delete_attr", "delete_global",                                       
                                        "load_const", "store_fast", "load_name", "load_global", 
                                        "store_global", "load_fast", "call_function", "print_item",
                                        "print_newline", "load_attr", "store_subscr", "import_name",
                                        "import_from", "setup_loop", "setup_except", "setup_finally",
                                        "compare_op", "pop_jump_if_false", "pop_jump_if_true",
                                        "jump_if_true_or_pop", "jump_if_false_or_pop",
                                        "jump_forward", "jump_absolute", "build_tuple",
                                        "make_function", "build_class", "build_list",
                                        "build_set", "build_map", "for_iter",
                                        "list_append", ))
        single_address_operations = []                                        
        for prefix in ("binary", "inplace"):
            for operation in ("power", "multiply", "divide", "floor_divide", "true_divide", "modulo",
                              "add", "subtract", "lshift", "rshift", "and", "xor" ,"or"):
                method = "{}_{}".format(prefix, operation)
                operation_code = dis.opmap[method.upper()]
                self.operation_handlers[operation_code] = getattr(self, method)
                single_address_operations.append(operation_code)
        for name in ("PRINT_ITEM", "PRINT_NEWLINE", "STORE_SUBSCR", "BUILD_CLASS",
                     "GET_ITER", "POP_TOP"):
            single_address_operations.append(dis.opmap[name])
        self.single_address_operations = set(single_address_operations)
        
    def execute_code(self, code_object, frame):
        bytecode = bytearray(code_object.co_code)
        index = 0
        opname = dis.opname
        single_address_operations = self.single_address_operations
        function_call_operations = set(dis.opmap[name] for name in 
                                       ("CALL_FUNCTION", "CALL_FUNCTION_VAR", "CALL_FUNCTION_KW",
                                        "CALL_FUNCTION_VAR_KW"))
        bytecode_length = len(bytecode)
        stack = frame.stack
        while index < bytecode_length:
            operation = bytecode[index]
            if operation == 83: # return top of stack item
                return stack.pop()
            self.alert("Performing: {}", (opname[operation], ), level=0)
            try:
                self.operation_handlers[operation]((bytecode[index + 1] if operation not in 
                                                    function_call_operations else
                                                    (bytecode[index + 1], bytecode[index + 2])),
                                                    code_object, stack, frame)
            except KeyError:
                if operation in self.operation_handlers:
                    raise
                message = "Operation not yet supported: {} {}".format(operation, dis.opname[operation])
                self.alert(message, level=0)
                raise RuntimeError(message)
            if self._delta:
                index += self._delta
                self._delta = 0
            if self._bytecode_counter is not None:
                index = self._bytecode_counter
                self._bytecode_counter = None
            else:
                index += 1 if operation in single_address_operations else 3
    
    def store_name(self, argument, code_object, stack, frame):
        frame.locals[code_object.co_names[argument]] = stack.pop()
        
    def delete_name(self, argument, code_object, stack, frame):
        del frame.locals[code_object.co_names[argument]]
        
    def unpack_sequence(self, argument, code_object, stack, frame):
        top_of_stack = stack.pop()
        for x in range(argument):
            stack.append(stack.pop())
            
    def dup_topx(self, argument, code_object, stack, frame):
        stack.extend(stack[-argument:])
 
    def store_attr(self, argument, code_object, stack, frame):
        setattr(stack.pop(), code_object.co_names[argument], stack.pop())
        
    def delete_attr(self, argument, code_object, stack, frame):
        delattr(stack.pop(), code_object.co_names[argument])
        
    def load_const(self, argument, code_object, stack, frame):    
        stack.append(code_object.co_consts[argument])
        
    def store_fast(self, argument, code_object, stack, frame):
        frame.locals[code_object.co_varnames[argument]] = stack.pop()
    
    def load_fast(self, argument, code_object, stack, frame):
        stack.append(frame.locals[code_object.co_varnames[argument]])
        
    def load_name(self, argument, code_object, stack, frame):
        stack.append(frame.locals[code_object.co_varnames[argument]])
        
    def load_global(self, argument, code_object, stack, frame):
        _globals = frame.parent.func_globals
        name = code_object.co_names[argument]
        try:
            stack.append(_globals[name])
        except KeyError:
            try:
                stack.append(_globals["__builtins__"][name])
            except (AttributeError, KeyError):
                raise NameError("global name '{}' not defined".format(name))
            
    def store_global(self, argument, code_object, stack, frame):
        frame.parent.func_globals[code_object.co_names[argument]] = stack.pop()
    
    def delete_global(self, argument, code_object, stack, frame):
        del frame.parent.func_globals[code_object.co_names[argument]]
        
    def call_function(self, argument, code_object, stack, frame):
        positional_arg_count, keyword_arg_count = argument
        #print "number of arguments: ", keyword_arg_count, positional_arg_count
        keywords = dict(((stack.pop(-2), stack.pop()) for 
                          count in range(keyword_arg_count)))
        arguments = tuple(stack.pop() for count in range(positional_arg_count))
        print "Arguments: ", arguments, keywords, stack[-1]
        stack.append(stack.pop()(*reversed(arguments), **keywords))
    
    def print_item(self, argument, code_object, stack, frame):
        sys.stdout.write(str(stack.pop()))
        sys.stdout.flush()
        
    def print_newline(self, argument, code_object, stack, frame):
        sys.stdout.write("\n")
        sys.stdout.flush()
        
    def load_attr(self, argument, code_object, stack, frame):
        stack.append(getattr(stack.pop(), code_object.co_names[argument]))
    
    def store_subscr(self, argument, code_object, stack, frame):
        stack.pop()[stack.pop()] = stack.pop()
    
    def delete_subscr(self, argument, code_object, stack, frame):
        del stack[-2][stack[-1]]
        
    def compare_op(self, argument, code_object, stack, frame):
        operator = dis.cmp_op[argument]
        left_operand = stack.pop()
     #   print "comparing: {} {} {}".format(stack[-1], operator, left_operand)
        try:
            operation = self._method_name[operator]
        except KeyError:
            if "is" in operator:
                value = left_operand is stack.pop()
                if "not" in operator:
                    value = not value
            elif operator == "not in":
                value = left_operand not in stack.pop()                
            elif operator == "exception_match":
                value = isinstance(left_operand, stack.pop())            
        else:
            value = getattr(left_operand, operation, left_operand.__cmp__)(stack.pop())
        stack.append(value)
    
    def pop_jump_if_false(self, argument, code_object, stack, frame):
        if not stack.pop():
            self._bytecode_counter = argument
            
    def pop_jump_if_true(self, argument, code_object, stack, frame):
        if stack.pop():
            self._bytecode_counter = argument
            
    def jump_if_true_or_pop(self, argument, code_object, stack, frame):
        if stack[-1]:
            self._bytecode_counter = argument
        else:
            del stack[-1]
            
    def jump_if_false_or_pop(self, argument, code_object, stack, frame):
        if not stack[-1]:
            self._bytecode_counter = argument
        else:
            del stack[-1]
            
    def jump_forward(self, argument, code_object, stack, frame):
        self._delta = argument
        
    def jump_absolute(self, argument, code_object, stack, frame):
        self._bytecode_counter = argument
    
    def build_tuple(self, argument, code_object, stack, frame):
        stack.append(tuple(stack[-argument:]))
        del stack[-argument - 1:-1]
        
    def make_function(self, argument, code_object, stack, frame):
        defaults = tuple(stack[-(count + 1)] for count in range(argument))
        stack.append(types.FunctionType(stack.pop(), globals(), argdefs=defaults))
            
    def build_class(self, argument, code_object, stack, frame):
        new_class = types.ClassType(stack[-3], stack[-2], stack[-1])       
    
    def build_list(self, argument, code_object, stack, frame):
        stack.append(list(stack[-argument:]))
        del stack[-argument - 1:-1]
        
    def build_set(self, argument, code_object, stack, frame):
        stack.append(set(stack[-argument:]))
        del stack[-argument - 1:-1]
        
    def build_map(self, argument, code_object, stack, frame):
        stack.append(dict())
        
    def get_iter(self, argument, code_object, stack, frame):
        stack.append(iter(stack.pop()))
     
    def for_iter(self, argument, code_object, stack, frame):
        print stack
        try:
            stack.append(next(stack[-1]))
        except StopIteration:
            del stack[-1]
            self._delta = argument
    
    def list_append(self, argument, code_object, stack, frame):
        list.append(stack[-argument - 1], stack.pop())
    
    def pop_top(self, argument, code_object, stack, frame):
        del stack[-1]
        
    def rot_two(self, argument, code_object, stack, frame):
        stack.append(stack.pop(-2))
        
    def rot_three(self, argument, code_object, stack, frame):
        stack.insert(-3, stack.pop())
    
    def rot_four(self, argument, code_object, stack, frame):
        stack.insert(-4, stack.pop())
        
    def dup_top(self, argument, code_object, stack, frame):
        stack.append(stack[-1])        
       
    def unary_positive(self, argument, code_object, stack, frame):
        stack[-1] = +stack[-1]
        
    def unary_negative(self, argument, code_object, stack, frame):
        stack[-1] = -stack[-1]
        
    def unary_not(self, argument, code_object, stack, frame):
        stack[-1] = not stack[-1]
        
    def unary_convert(self, argument, code_object, stack, frame):
        stack[-1] = `stack[-1]`
        
    def unary_invert(self, argument, code_object, stack, frame):
        stack[-1] = ~stack[-1]
     
    def slice_0(self, argument, code_object, stack, frame):
        stack[-1] = stack[-1][:]
        
    def slice_1(self, argument, code_object, stack, frame):
        stack[-1] = stack[-2][stack[-1]:]
        
    def slice_2(self, argument, code_object, stack, frame):
        stack[-1] = stack[-2][:stack[-1]]
    
    def slice_3(self, argument, code_object, stack, frame):
        stack[-1] = stack[-3][stack[-2]:stack[1]]
        
    def store_slice_0(self, argument, code_object, stack, frame):
        stack[-1][:] = stack[-2]
        
    def store_slice_1(self, argument, code_object, stack, frame):
        stack[-2][stack[-1]:] = stack[-3]
        
    def store_slice_2(self, argument, code_object, stack, frame):
        stack[-2][:stack[-1]] = stack[-3]
        
    def store_slice_3(self, argument, code_object, stack, frame):
        stack[-3][stack[-2]:stack[-1]] = stack[-4]
        
    def delete_slice_0(self, argument, code_object, stack, frame):
        del stack[-1][:]
        
    def delete_slice_1(self, argument, code_object, stack, frame):
        del stack[-2][stack[-1]:]
        
    def delete_slice_2(self, argument, code_object, stack, frame):
        del stack[-2][:stack[-1]]
        
    def delete_slice_3(self, argument, code_object, stack, frame):
        del stack[-3][stack[-2]:stack[-1]]
        
    def print_expr(self, argument, code_object, stack, frame):
        print stack.pop()
        
    def print_item_to(self, argument, code_object, stack, frame):
        stack.pop().write(str(stack.pop()))
        
    def print_newline_to(self, argument, code_object, stack, frame):
        stack.pop().write('\n')
        
    def break_loop(self, argument, code_object, stack, frame):
        raise NotImplementedError()
    
    def continue_loop(self, argument, code_object, stack, frame):
        self._bytecode_counter = argument
    
    def load_locals(self, argument, code_object, stack, frame):
        stack.append(frame.locals())
        
    def yield_value(self, argument, code_object, stack, frame):
        raise NotImplementedError
        stack.pop()
        
    def import_star(self, argument, code_object, stack, frame):
        _locals = frame.locals
        module = stack[-1]
        for attribute_name in dir(module):
            if not attribute_name.startswith('_'):
                _locals[attribute_name] = getattr(attribute_name, module)
        stack.pop()
        
    def exec_stmt(self, argument, code_object, stack, frame):
        _locals = _globals = None
        try:
            code = stack.pop(-3)
        except IndexError:
            try:
                code = stack.pop(-2)
            except IndexError:
                code = stack.pop(-1)                
            else:
                _locals = stack.pop()                
        else:
            _locals = stack.pop(-2)
            _globals = stack.pop()
        exec code in _locals, _globals
     
    def pop_block(self, argument, code_object, stack, frame):
        raise NotImplementedError
        
    def end_finally(self, argument, code_object, stack, frame):
        raise NotImplementedError
        
    def setup_with(self, argument, code_object, stack, frame):
        raise NotImplementedError
        
    def with_cleanup(self, argument, code_object, stack, frame):
        raise NotImplementedError
        
    def import_name(self, argument, code_object, stack, frame):
        __import__(code_object.co_names[argument], stack.pop(), stack.pop())
        
    def import_from(self, argument, code_object, stack, frame):
        stack.append(getattr(stack[-1], code_object.co_names[argument]))
    
    def setup_loop(self, argument, code_object, stack, frame):
        raise NotImplementedError
        
    def setup_except(self, argument, code_object, stack, frame):
        raise NotImplementedError
        
    def setup_finally(self, argument, code_object, stack, frame):
        raise NotImplementedError
        
        
    @pride.preprocess
    def generate_binary_inplace_methods():
        source = []
        method_source = "def {}_{}(self, argument, code_object, stack, frame):\n\tstack.append(stack.pop() {} stack.pop())"
        subscr_source = "def {}_subscr(self, argument, code_object, stack, frame):\n\tstack.append(stack.pop()[stack.pop()])"
        operations = {"power" : "**", "multiply" : '*', "divide" : '/', 
                      "floor_divide" : "//",  "true_divide" : '/', "modulo" : '%', 
                      "add" : '+', "subtract" : '-', "lshift" : "<<", 
                      "rshift" : ">>", "and" : '&', "xor" : '^', "or" : '|'}
        for operation_name, symbol in operations.items():
            source.append(method_source.format("binary", operation_name, symbol))
            source.append(method_source.format("inplace", operation_name, symbol))
        source.append(subscr_source.format("binary"))
        source.append(subscr_source.format("inplace"))
        source.append('\n')
        return '\n    '.join(source)
    
def _test(keyword=True, *args, **kwargs):
    print keyword, args, kwargs
    return None
    
def test_bytecode_interpreter():        
    def test(first_argument, default_argument=True, *args, **kwargs):
        print first_argument
        a_variable = _test(False, 1, 2, testing='yes')
        internal_local = "test_string"
        global X
        X += 10
        first_argument += X
        print ''.join(args)
        kwargs["test_key"] = "value"
        if 'value' in kwargs:
            class Test_Definition2(object):
                @classmethod
                def _test_method1(cls):
                    print "Inside _test_method1", cls
           # print "Built class: ", Test_Definition2
            def _subtest():
                pass
        [pow(x, 2) for x in xrange(10)]#(range(y) for y in xrange(10))]
        return 1
    interpreter = Bytecode_Interpreter()
    function = Function.wrap_function(test)
   # dis.dis(test)
    assert function(10) == 1
    
if __name__ == "__main__":
    test_bytecode_interpreter()