import socket

import pride.base

class Static_Wrapper(pride.base.Base):
    
    wrapped_attributes = tuple()
    wrapped_object_name = ''
    
    defaults = {"wrapped_object" : None}
    
    def __init__(self, **kwargs):
        super(Static_Wrapper, self).__init__(**kwargs)
        if self.wrapped_object:
            self.wraps(self.wrapped_object)
            
    def wraps(self, _object):
        if self.wrapped_attributes:
            for attribute in self.wrapped_attributes:
                setattr(self, attribute, getattr(_object, attribute))
        else:
            for attribute in dir(_object):
                if "__" != attribute[:2] and "__" != attribute[:-2]:
                    setattr(self, attribute, getattr(_object, attribute))
                
        self.wrapped_object = _object
        if self.wrapped_object_name:
            setattr(self, self.wrapped_object_name, _object)
            
        
class Socket_Wrapper(Static_Wrapper):
            
    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket())
        super(Socket_Wrapper, self).__init__(**kwargs)
        
#s = Socket_Wrapper()
#s.connect((socket.gethostbyname("google.com"), 80))
#print s.getpeername()        
#s.close()

def test1():
    s = Socket_Wrapper()
    for x in xrange(1000000):
        s.connect
import pride.network
        
def test2():
    s = pride.network.Socket(add_on_init=False)
    for x in xrange(1000000):
        s.connect
        
import pride.decorators
print pride.decorators.Timed(test1, 1)()
print pride.decorators.Timed(test2, 1)()