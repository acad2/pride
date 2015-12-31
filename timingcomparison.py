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
        
import pride.decorators

def timing_comparison(*functions, **kwargs):
    iterations = kwargs.get("iterations", 1)
    for function, args, kwargs in functions:
        print pride.decorators.Timed(function, iterations)(*args, **kwargs)
        
timing_comparison((global_access, tuple(), {}), (attribute_access, tuple(), {}))        