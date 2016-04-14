import pride.decorators

def timing_comparison(*functions, **kwargs):
    iterations = kwargs.get("iterations", 1)
    for function, args, kwargs in functions:
        print pride.decorators.Timed(function, iterations)(*args, **kwargs)

# test accessing global versus accessing an attribute; global is faster        
TEST = "this is a test string"
def global_access():
    for x in xrange(10000):
        TEST
 
class _Test(object):
    def __init__(self):
        self.TEST = "this is a test string"
        
def attribute_access():
    t = _Test()
    for x in xrange(10000):
        t.TEST
          
#timing_comparison((global_access, tuple(), {}), (attribute_access, tuple(), {}))        
      
def number_of_set_bits(i):
    i = i - ((i >> 1) & 0x55555555)
    i = (i & 0x33333333) + ((i >> 2) & 0x33333333)
    return (((i + (i >> 4)) & 0x0F0F0F0F) * 0x01010101) >> 24
    
def number_of_set_bits_sum(x):
    return sum( [x&(1<<i)>0 for i in range(8)] )

timing_comparison((number_of_set_bits, (127, ), {}), (number_of_set_bits_sum, (127, ), {}))