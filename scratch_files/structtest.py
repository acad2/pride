import mpre.tests.attributetest 
Struct = mpre.tests.attributetest.Struct
import mpre.base
import mpre.misc.decoratorlibrary
Timed = mpre.misc.decoratorlibrary.Timed

from cPickle import dumps

base = mpre.base.Base()
dictionary = base.__dict__
print "struct creation time: ", Timed(Struct, iterations=10000)(dictionary)
print "cpickle dumps time  : ", Timed(dumps, iterations=10000)(dictionary)