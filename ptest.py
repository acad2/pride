import textwrap
import re
import inspect
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
    
import mpre.utilities

def run_functions(function_arguments):

    # unpack arguments
    whatever_arg1, whatever_testing, whatever_kwargs = function_arguments.pop(0)
    
    print "stuff"
    
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
    method_source = inspect.getsource(method)
    end_of_def = method_source.index(":")
    start_of_source = method_source[end_of_def:].index("\n")
    
    # ensure source begins indented by one block
    method_source = textwrap.dedent(method_source[end_of_def +
                                    start_of_source:]).strip()
    method_source = indent_lines(method_source)
            
    argument_names = method.__code__.co_varnames
    for name in argument_names:
        for slice in find_token_indices(name, method_source):
            method_source = re.sub(r'\b' + name + r'\b', 
                                   ''.join((component, '_', method_name,
                                            '_', name)), 
                                   method_source)                
    
    for start, end in find_token_indices("return", method_source):
    #    newline_index = method_source[end:].index('\n')
        method_source = re.sub(r'\b' + "return" + r'\b',
                               ''.join((method_name, '_', 
                                        "Processor._return(",
                                        component, '_', method_name, ', ')),
                               method_source)
    return method_source
  #  print method_source            
    
class Preemptive_Instruction(object):
        
    def __init__(self, *args):
        callbacks = self.callbacks = {}
        source = ["def {}"]
        # create inlined function with function named prefixed to variable names
        for instruction in args:
            component = '' #instruction.component
            method_name = instruction.__name__ #instruction.method
            method = instruction #getattr(mpre.objects[component], method)
         #   callbacks[(component, method_name)] = instruction.callback
            source.append(inline_function_source(method, method_name, component))
        print '\n'.join(source)
        
    def _return(function_name, *args):
        self.callbacks[function_name](*args)
        
        
if __name__ == "__main__":
    def test(testing, idek=True, *args, **kwargs):
        return None
    instruction = Preemptive_Instruction(run_functions, test)