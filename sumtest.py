class Test(object):
    
    def __init__(self, _data):
        self._data = _data
        
    def _get_data(self):
        if self._data:
            data = self._data
        else:
            data = self._data
            data += 1
            data -= 1
            data *= 1
            data /= 1
        return data
    def _set_data(self, value):
        self._data = value
    data = property(_get_data, _set_data)
    
def test_sum():
    tests = [Test(x) for x in xrange(100)]
    for x in xrange(1000):
        sum((test.data for test in tests))
        
        
class Test2(object):
            
    def __init__(self, data):
        self.data = data        
        
def test_inline():
    tests = [Test2(x) for x in xrange(100)]
    for x in xrange(1000):
        _sum = 0
        for test in tests:
            data = test.data
            data += 1
            data -= 1
            data *= 1
            data /= 1
            _sum += data
        
from pride.decorators import Timed

print Timed(test_sum, 10)()
print Timed(test_inline, 10)()        