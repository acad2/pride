import hashlib
import textwrap
import re
import inspect
import hashlib
import string
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
    
import mpre.utilities

def printable_hash(object, output_size=20):
    """ Returns a hash of an object where the output characters are members
        of the set of upper and lowercase ascii letters, and digits. """
    allowed_characters = set(string.letters + string.digits)
    result = []
    new_values = object
    while len(result) < output_size:
        new_values = hashlib.sha256(str(new_values)).digest()
        result.extend((item for item in new_values if item in allowed_characters))
    return ''.join(result[:output_size])
    
def get_arg_count(function):
    try:
        func_code = function.im_func.func_code
    except AttributeError:
        func_code = function.func_code
    return len(inspect.getargs(func_code).args)    
    
def run_functions(function_arguments): # just a test function

    # unpack arguments
    whatever_arg1, whatever_testing, whatever_kwargs = function_arguments.pop(0)
    
    print "stuff"
    testreturn = None
    whatever_return = whatever_arg1
    if True:
        print "This is a test branch"
        if False:
            print "This won't happen"

def indent_lines(string, amount=1, spacing="    "):
    return '\n'.join(spacing * amount + line for line in string.split('\n'))     
           
def inline_function_source(method, method_name, component=''):
    full_name = ''.join((component, '_', method_name))
    method_source = inspect.getsource(method)
    end_of_def = method_source.index(":")
    start_of_source = method_source[end_of_def:].index("\n")
    
    # ensure source begins indented by one block
    method_source = textwrap.dedent(method_source[end_of_def +
                                    start_of_source:]).strip()
    method_source = indent_lines(method_source)
            
    argument_names = method.__code__.co_varnames
    
    for name in argument_names:
        new_name = full_name + '_' + name
        declaration = "{} = {}_namespace.{}".format(new_name, full_name, name)
        #print "Replacing {} with {}".format(name, new_name)
        method_source = mpre.importers.Parser.replace_symbol(name, method_source, new_name)               
 
    method_source = mpre.importers.Parser.replace_symbol('return', method_source, 
                          "$Preemptive_Multiprocessor._return['{}'] =".format(full_name)) 
    return method_source            
            
            
class Preemptive_Multiprocessor(mpre.base.Base):
    
    def __init__(self, **kwargs):
        self.threads = []
        self._combination_cache, self._return = {}, {}
        super(Preemptive_Multiprocessor, self).__init__(**kwargs)
        
    def run(self):
        threads = tuple((item[0] for item in self.threads))
        arguments = []
        for _, args in self.threads:
            arguments.extend(args)
        new_function_name = printable_hash(threads)
        header = "def function_{}(".format(new_function_name)
        source = []
        if threads not in self._combination_cache:
            last_index = len(threads) - 1
            for count, _thread in enumerate(threads):
                source.append(_thread.source)
                _header = mpre.utilities.function_header(_thread.method)[1:-1] # remove the ( )
                __header = []                
                prefix = _thread.component_name + '_' + _thread.method_name + '_'
                for argument_name in _header.split():
                    if argument_name[0] == '*':
                        if argument_name[1] == '*':
                            argument_name = prefix + argument_name[2:]
                        else:
                            argument_name = prefix + argument_name[1:]
                    else:
                        argument_name = prefix + argument_name
                    __header.append(argument_name)
                header += ' '.join(__header)
                if count != last_index:
                    header += ', '
            
            header += '):'        
        #    print header
            source.insert(0, header)
            source.append("\n    return locals()")
            context = globals().copy()
            code = mpre.compiler.compile('\n'.join(source), "<string>")
            exec code in context, context
            function = self._combination_cache[threads] = context["function_" + new_function_name]
        else:
            function = self._combination_cache[threads]
        print function, mpre.utilities.function_header(function)
        print arguments
        function(*arguments)
        
    
class Thread(mpre.base.Base):
        
    defaults = {"component_name" : '', "method_name" : '', "callback" : None,
                "source" : ''}
    
  # def __new__(cls, *args, **kwargs):
  #     try:
  #         method = kwargs["method"]
  #     except:
  #         method_name = kwargs["method_name"]
  #         component = mpre.objects[kwargs["component_name"]]
  #         method = getattr(component, method_name)
  #     header = mpre.utilities.function_header(method)
  #     _source = "def " + method.__name__ + header + ':'
        
    def __init__(self, **kwargs):
        super(Thread, self).__init__(**kwargs)
        component_name, method_name = self.component_name, self.method_name
        if not self.method:            
            self.method = getattr(mpre.objects[component_name], method_name)
        self.source = inline_function_source(self.method, method_name, component_name)
        self.arg_count = get_arg_count(self.method)
        
    def __call__(self, *args, **kwargs):
        _arguments, _args = args[:self.arg_count], args[self.arg_count:]
        if _args:
            if kwargs:
                packed_args = _arguments + (_args, kwargs)
            else:
                packed_args = _arguments + (_args, )
        elif _arguments:
            if kwargs:
                packed_args = _arguments + (kwargs, )
            else:
                packed_args = _arguments
        elif kwargs:
            packed_args = (kwargs, )
        else:
            packed_args = tuple()        
        mpre.objects["Preemptive_Multiprocessor"].threads.append((self, packed_args))
        
if __name__ == "__main__":
    def test(testing, idek=True, *args, **kwargs):
        print "Inside test :)"
        return None
    thread = Thread(method=test)
    thread2 = Thread(method=run_functions)
    p = Preemptive_Multiprocessor()
    thread(1, False, 2, 3, 4, 5, woo="hooray")
    thread2([(1, 2, 3)])
    p.run()