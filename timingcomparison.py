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

#timing_comparison((number_of_set_bits, (127, ), {}), (number_of_set_bits_sum, (127, ), {}))
    
def inplace_add_inplace_and(a, b):
    a += b
    a &= 255
    
def reallocate_add_and(a, b):
    a = (a + b) & 255
    
#timing_comparison((inplace_add_inplace_and, (1, 10), {}), (reallocate_add_and, (1, 10), {}), iterations=1000000)

def list_replace(_list, index, value):
    _list[index] = value
    
def bytearray_replace(_bytearray, index, value):
    _bytearray[index] = value
    
#timing_comparison((list_replace, ([0] * 256, 128, 65536), {}), 
#                  (bytearray_replace, ([0] * 256, 128, 255), {}), iterations=100000) 