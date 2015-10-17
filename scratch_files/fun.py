import hashlib
import random

import pride.base

class _Object(pride.base.Base):
    
    defaults = pride.base.Base.defaults.copy()
    
    def __add__(self, other_self):
        self_class, other_class = self.__class__, other_self.__class__
        
        new_name = '_'.join((self_class.__name__, other_class.__name__))
        
        new_class_attributes = self_class.__dict__.copy()
        new_class_attributes.update(other_class.__dict__)
        
        new_class = type(new_name, tuple(set((self_class, other_class))),
                         new_class_attributes)
                         
        new_self_attributes = self.__dict__.copy()
        new_self_attributes.update(other_self.__dict__)
        return new_class(**new_self_attributes)
        
        
def generate_function(input0=0, input1=0, operation_count=0,
                      operators=("+=", "-=", "*=", "/=", "//=", "**=", "%=",
                                 "^", "&=", "^=", "<<=", ">>="),
                      operations=tuple()):
    hash_string = hashlib.sha1(':'.join(str(item) for item in 
                              (input0, input1, operation_count, 
                              operators, operations))).hexdigest()                     
    input0 = input0 or random.randint(1, 8)
    input1 = input1 or random.randint(1, 8)
    function_name = "generated_function{}".format(hash_string)
    source = "def {}(input0={}, input1={}):\n".format(function_name, input0, input1)
    inputs = ("input0", "input1")
    for count in xrange(operation_count or random.randint(1, 6)):
        operator = random.choice(operators)
        source += "    {} {} {}\n".format(random.choice(inputs), 
                                          operator, 
                                          random.choice(inputs))
    source += "    return input0, input1"
    print "Created: \n", source
    namespace = {}
    exec compile(source, 'generate_function', 'exec') in namespace, namespace
    return namespace.pop(function_name)
        
        
if __name__ == "__main__":
    object1 = _Object(thisisatest=1)
    object2 = _Object(again=None)
    
    object3 = object1 + object2
    print object3.__dict__
    print object3.__class__.__mro__
    
    new_function = generate_function()