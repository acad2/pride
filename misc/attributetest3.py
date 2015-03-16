import mmap
import cPickle as pickle

import mpre.base as base
import mpre.fileio as fileio


class Persistent_Reactor(base.Reactor):
    
    memory = {}
    
    def __new__(cls, *args, **kwargs):
        instance = super(Persistent_Reactor, cls).__new__(cls, *args, **kwargs)
        super_object = super(cls, instance)
        set_attribute = super_object.__setattr__
        get_attribute = super_object.__getattribute__
        
        fileio.ensure_file_exists(instance.instance_name)
        _file = fileio.File(instance.instance_name, 'r+b')
        memory = mmap.mmap(_file.fileno(), 65535)        
        
        set_attribute("file", _file)
        Persistent_Reactor.memory[instance] = memory
        
        try:
            dictionary = pickle.load(memory)
        except EOFError:
            instance.__init__(*args, **kwargs)
            dictionary = get_attribute("__dict__")
            pickle.dump(dictionary, memory)
            memory.flush()
        else:
            get_attribute("__dict__").update(dictionary)

        return instance
        
    def __getattribute__(self, attribute):
        print "inside getattribute", attribute
        try:            
            memory = Persistent_Reactor.memory[self]
            memory.seek(0)
            print "getting shared attribute: ", attribute
            return pickle.load(memory)[attribute]
        except KeyError:
            print "getting local attribute: ", attribute
            return super(Persistent_Reactor, self).__getattribute__(attribute)
        
    def __setattr__(self, attribute, value):
        print "setting attribute: ", attribute
        try:
            memory = Persistent_Reactor.memory[self]
            memory.seek(0)
            
            dictionary = pickle.load(memory)
            dictionary[attribute] = value
            print "setting shared attribute: ", attribute, value
            memory.seek(0)
            pickle.dump(dictionary, memory)
            memory.flush()
        except KeyError:
            print "set regular attribute", attribute, value
            super(Persistent_Reactor, self).__setattr__(attribute, value)
        
if __name__ == "__main__":
    persistent = Persistent_Reactor()
    #persistent.x = "testing"