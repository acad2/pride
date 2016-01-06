class Child_Object(object):
            
    def __init__(self, wrapped_object=None):
        super(Child_Object, self).__setattr__("wrapped_object", wrapped_object)
        
    def __getattribute__(self, attribute):
        return getattr(super(Child_Object, self).__getattribute__("wrapped_object"), attribute)
        
    def __setattr__(self, attribute, value):
        if attribute == "wrapped_object":
            super(Child_Object, self).__setattr__(attribute, value)
        else:
            wrapped_object = super(Child_Object, self).__getattribute__("wrapped_object")
            setattr(wrapped_object, attribute, value)
        
        
class BlackBox():
    
    def __init__(self):
        self.__dict__[5] = Child_Object()
        self.bar = Child_Object()
                
    def get(self, item):
        return self.__dict__[item]
        
    def resolve(self):
        self.__dict__[5].wrapped_object = 5
        self.bar.wrapped_object = "bar"        
        

        
foo = BlackBox()
bar1 = foo.get(5)      
bar2 = foo.get("bar")

print (bar1, bar2)

foo.resolve()

print (bar1 + 5, bar2 + "test")  