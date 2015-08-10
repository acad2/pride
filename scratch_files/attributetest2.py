import mmap
import cPickle as pickle

import mpre.base
import mpre.fileio as fileio

class Persistent_Reactor(mpre.base.Base):
    
    def __init__(self, **kwargs):
        super(Persistent_Reactor, self).__init__(**kwargs)
        file = self.file = fileio.File(self.instance_name, "r+b")
        memory = memory = mmap.mmap(file.fileno(), 65535)
        memory.seek(0)
        
        try:
            current_state = pickle.load(memory)
        except:
            current_state = dict((attribute, value) for attribute, value in
                                  self.__dict__.items())
            print "dumping state to memory: ", current_state
            pickle.dump(current_state, memory)
            memory.flush()
        else:
            for attribute, value in current_state.items():
                self.alert("updating state; {} = {}",
                           [attribute, value],
                           0)
                setattr(self, attribute, value)
                
        self.memory = memory
        print "changing descriptors"
        self.__getattribute__ = self.persistent_getattribute
        self.__setattr__ = self.persistent_setattr
     
    def __getstate__(self):
        dict_copy = self.__dict__.copy()
        del dict_copy["memory"]
        return dict_copy
        
    def __setstate__(self, state):
        self.__init__(**state)
        return self
        
    def persistent_getattribute(self, attribute):
        print "i never happen"
        raise SystemExit
        get_attribute = super(Persistent_Reactor, self).__getattribute__
        print "getting attribute: ", attribute
        value = get_attribute(self, "value")
        memory = get_attribute(self, "memory")
        memory.seek(0)
        old_copy = pickle.load(memory)
        
        if attribute in old_copy:
            shared_value = old_copy[attribute]
            if shared_value != value:
                super(Persistent_Reactor, self).__setattr__(attribute, shared_value)
                value = shared_value
                
        return value
        
    def persistent_setattr(self, attribute, value):
        super_object = super(Persistent_Reactor, self)
        
        super_object.__setattr__(attribute, value)
        
        memory = super_object.__getattribute__("memory")
        memory.seek(0)
        old_copy = pickle.load(memory)
        
        old_copy[attribute] = value
        memory.seek(0)
        pickle.dump(value, memory)
        
        
if __name__ == "__main__":
    import unittest

    class Test_Persistent_Reactor(unittest.TestCase):
        
        def test_get_set(self):
            reactor = Persistent_Reactor(boolean=True, 
                                         string="this is a shared memory string",
                                         integer=1337, 
                                         decimal=1.0, 
                                         complex=mpre.base.Base())
            
            assert reactor.__getattribute__ is reactor.persistent_getattribute
            self.failUnless(reactor.boolean is True)
            self.failUnless(reactor.string is "this is a shared memory string")
            self.failUnless(reactor.integer is 1337)
            self.failUnless(reactor.decimal == 1.0)
            self.failUnless(isinstance(reactor.complex, mpre.base.Base))
    
    unittest.main()
            