data = '\x01' * 4096

def _test_memoryview2():
    m = memoryview(data)
    while True:
        yield m[:4096]
     
thread = _test_memoryview2()
def test_memoryview2():
    next(thread)
    
def test_string():
    return data[:4096]
    
def test_memoryview():
    return memoryview(data)[:4096]
    
from mpre.misc.decoratorlibrary import Timed

print "slice time: ", Timed(test_string, iterations=100000)()
print "memoryview: ", Timed(test_memoryview, iterations=100000)()    
print "memory2   : ", Timed(test_memoryview2, iterations=100000)()