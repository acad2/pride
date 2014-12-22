Tracking instances and __new__

The __init__ method of python objects is often mistakenly referred to as the
constructor. This idea is usually close enough for rock and roll, but it is
not technically true. When the __init__ method is called, the object already
exists. This is evident by the fact that self is actually an argument to
the call to __init__:

    ...
    def __init__(self, arguments):
    ...

When an object is instantiated, there is a method that is called before __init__.
This method is __new__. This method is not normally needed for basic things like
assigning attributes to the instance - such things should be done in __init__, 
not __new__. The implicit call to __new__ - the one that has been called every
time you have instantiated an object that you may have not known about - effectively 
does something similar to the following:

    class Base(object):
    
        def __new__(cls, *args, **kwargs):
            return super(Base, cls).__new__(cls, *args, **kwargs)
            
The return value of the method actually returns the newly created object.            
So what *would* we need to use this for? One of the use cases is tracking
instances. When an instance is created, we can give it a number and associate
this number with the instance:
                
    class Base(object):
    
        instance_count = 0
        
        def __new__(cls, *args, **kwargs):
            instance = super(Base, cls).__new__(cls, *args, **kwargs)
            instance_number = instance.instance_number = cls.instance_count
            cls.instance_tracker[instance_number] = instance
            cls.instance_count += 1
            return instance

    >>> b = base.Base()
    >>> b.instance_number
    >>> 0
    >>> base.Base.instance_tracker[0]
    >>> <base.Base object at 0x01D35830>
    
We can also use a property attribute to tie together the class name of the
object with its number to produce a name for the object. A property is 
effectively a calculated attribute. It takes up to three arguments - a method 
to be called when getting, setting, or deleting the attribute in question:

    class Base(object):
        
        def _get_name(self):
            return type(self).__name__ + str(self.instance_number)
        instance_name = property(_get_name)
        ...
        
Base objects will now have a name attribute that provides the class name
along with the instance number:
    
    >>> b = base.Base()
    >>> b.instance_name
    >>> 'Base0'
    
This is a string representation that is effectively unique to the object
in question. With a dictionary we can then map this unique name to the
object itself, and we can automatically populate this dictionary whenever
an object is instantiated:
    
    Component_Resolve = {}
    
    class Base(object):
        
        instance_count = 0
        
        defaults = {"memory_size" : 4096, "network_packet_size" : 8192}
        
        def _get_name(self):
            return type(self).__name__ + str(self.instance_number)
        instance_name = property(_get_name)
              
        def __new__(cls, *args, **kwargs):
            instance = super(Base, cls).__new__(cls, *args, **kwargs)
            instance_number = instance.instance_number = cls.instance_count
            cls.instance_tracker[instance_number] = instance
            cls.instance_count += 1
            return instance
            
        def __init__(self, **kwargs):
            options = self.defaults.copy()
            options.update(kwargs)
            self.attribute_setter(**options)
            Component_Resolve[self.instance_name] = self
            
    >>> base.Base() # instantiate but did not assign the result to a variable
    >>> b = Component_Resolve["Base0"]
    >>> b # got the created object anyways
    >>> <base.Base object at 0x01D35830>
    
Note how our defaults has included a memory size attribute that has not been used
yet. Python has a module called mmap, which supports memory mapping files that
reside on disk into memory. You can also map anonymous regions of memory which
do not have a relation to any file on disk. Doing so will yield an empty storage 
space that you can store arbitrary data in. We can setup our objects to have their
own little chunk of memory like so:
    
    Component_Memory = {}
    
    class Base(object):
        ...
        def __init__(self, **kwargs):
            ...
            Component_Memory[self.instance_name] = mmap.mmap(-1, self.memory_size)
            
The -1 supplied as the first argument indicates that we want an anonymous region
of memory that is not associated with a file on disk. Each base object will now
have 4kb of memory that any other object can write to. We can provide methods
for reading/writing from/to this memory:
            
    class Base(object):
        ...
        def send_to(self, component_name, message):
            Component_Memory[component_name].write(message+"delimiter")
        
        def read_messages(self):
            memory = Component_Memory[self.instance_name]
            memory.seek(0) # like a file, reads/writes changes the seek position
            data = memory.read(self.memory_size) # read the entire memory segment
            memory.seek(0)
            if data.count("delimiter"): # check to see if we got messages
                size = len(data) # read doesn't necessarily return memory_size bytes
                messages = data.split("delimiter")
                memory.write("\x00"*size) # make room for more messages
                memory.seek(0) # reset seek position
            else: # no messages received
                messages = [] 
            return messages
        
    >>> b = base.Base()
    >>> b.data = []
    >>> c = base.Base()
    >>> c.data = "this is a test message!"
    >>> c.send_to("Base0", c.data)
    >>> for message in b.read_messages():
    >>>     b.data.append(message)
    >>> ...
    >>> b.data
    >>> ["this is a test message!"]
    
While the test message isn't that impressive or interesting, the messaging 
scheme here is a matter of good form - while we could read c's data directly
and put it into b's data manually, it is best to have each object be responsible
for manipulating it's own data members. Good form often yields other benefits,
especially regarding manageability of code.