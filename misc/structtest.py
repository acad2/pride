from mpre.misc.attributetest import Struct
import mpre.base
from mpre.misc.decoratorlibrary import Timed
from cPickle import dumps

base = mpre.base.Base()
dictionary = base.__dict__
print "struct creation time: ", Timed(Struct, iterations=10000)(dictionary)
print "cpickle dumps time  : ", Timed(dumps, iterations=10000)(dictionary)