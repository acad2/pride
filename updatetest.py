import pickle
import sys
from types import MethodType

def update(instance):
    stats = pickle.dumps(instance)
    reload(sys.modules[instance.__module__])
    return pickle.loads(stats)       
    
def patch(method_name, _class, new_method):
    setattr(_class, method_name, MethodType(new_method, None, _class))
    
    
if __name__ == "__main__":
    import testclass
    instance = testclass.Test_Class(1, 2, 3, False)
    print "\noriginal method: "
    instance.testmethod()
    
    def patch(self, *args):
        print "something different"
        
    print "\nmonkey patched method: "
    instance.testmethod = MethodType(patch, instance, testclass.Test_Class)
    instance.testmethod()
    
    print "\nAlternate instance method post patch: "
    instance2 = testclass.Test_Class(1, 2, 3, True)
    instance2.testmethod()
    with open("testclass.py", 'w') as pyfile:
        pyfile.write("""class Test_Class(object):
        
    def __init__(self, x, y, z, test=True):
        self.x = x
        self.y = y
        self.z = z
        self.test = test
        
    def testmethod(self, *args):
        print "inside testmethod", self, args
        print "This method has been updated successfully"
        
    class_var = 1337""")
        pyfile.flush()
        pyfile.close()
    instance = update(instance)
    print "\ntestmethod after update"
    instance.testmethod()