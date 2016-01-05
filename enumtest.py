class Test(list):
    
    def __len__(self):
        print "Inside len! You won't see me"
        return 0       
            
            
try:    
    for count, item in enumerate(Test()):
        print count, item
    if not count:
        pass # triggers name error on empty sequence
except NameError:
    print "Itemless sequence"