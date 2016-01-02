class Test(object):
    
    def __init__(self):
        print "Inside Test init"
        
class Test2(Test):            
            
    def __init__(self):
        print "Inside Test2"
       
class Test3(Test2):
        
    def __init__(self):
        print "Inside Test3"
        
t = Test3.__new__(Test3)
Test.__init__(t)        