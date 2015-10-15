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
    
    
def run_functions(function_arguments):

    # unpack arguments
    whatever_arg1, whatever_testing, whatever_kwargs = function_arguments.pop(0)
    
    print "stuff"
    testreturn = None
    whatever_return = whatever_arg1
    if True:
        print "This is a test branch"
        if False:
            print "This won't happen"
    
def find_token_indices(token, string):
    return [m.span() for m in re.finditer(r'\b' + token + r'\b', string)]
    
def indent_lines(string, amount=1, spacing="    "):
    file_like_object = StringIO.StringIO(string)
    return ''.join(spacing + line for line in file_like_object.readlines())      
           
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
        method_source = mpre.importers.Parser.replace_symbol(name, method_source, new_name)               
 
    method_source = mpre.importers.Parser.replace_symbol('return', method_source, 
                          "Processor._return['{}'] =".format(full_name)) 
    return method_source
            
    
class Preemptive_Instruction(object):
        
    def __init__(self, *args):
        callbacks = self.callbacks = {}
        source = []
        header = "def function_{}(".format(printable_hash(args))
        # create inlined function with function named prefixed to variable names
        arguments = []
        last_index = len(args) - 1
        for count, instruction in enumerate(args):
            component = '' #instruction.component
            method_name = instruction.__name__ #instruction.method
            method = instruction #getattr(mpre.objects[component], method)
         #   callbacks[(component, method_name)] = instruction.callback
            source.append(inline_function_source(method, method_name, component))
            header += mpre.utilities.function_header(method)[1:-1] # remove ( )
            if count != last_index:
                header += ', '
            
        header += '):'
        source.insert(0, header)
        source.append("\n    return locals()")
        print '\n'.join(source)
        code = compile('\n'.join(source), 'auto_threader', "exec")
        
    def _return(function_name, *args):
        self.callbacks[function_name](*args)
        
        
if __name__ == "__main__":
    def test(testing, idek=True, *args, **kwargs):
        return None
    instruction = Preemptive_Instruction(run_functions, test)