def test_map():
    containers = ([1], [1, 2], [1, 2, 3])
    for x in xrange(10000):
        one, two, three = map(len, containers)

def test_genexp():
    containers = ([1], [1, 2], [1, 2, 3])
    for x in xrange(10000):
        one, two, three = (len(item) for item in containers)
        
from pride.decorators import Timed

print Timed(test_map, 10)()
print Timed(test_genexp, 10)()
