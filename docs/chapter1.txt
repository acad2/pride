Metaprogramming

The word root meta applies the word that follows to itself. Programming is the art
of writing code for computers. It follows then, that metaprogramming is the art
of writing code that writes code. This may sound somewhat challenging, but in reality
it sounds more intimidating then it really is. 

For example, a standard CPython class definition would look something like:

    class Base(object):
    
        def __init__(self, memory_size=8192, network_chunk_size=4096):
            self.memory_size = memory_size
            self.network_chunk_size = network_chunk_size
    
    >>> base_object = Base()
    >>> base_object.memory_size
    >>> 8192
    >>> base_object.network_chunk__size
    >>> 4096
    
There is actually quite a bit of repetition there. Did you notice that the terms
memory_size and network_chunk_size are used three times each? Repetition is 
where computers excel, so we should try to delegate repetitive jobs to the computer. 
We can rewrite this in a more succinct fashion and avoid repeating ourselves:
          
    base_defaults = {"memory_size" : 8192,
                     "network_chunk_size" : 4096}
                
    class Base(object):
                
        def __init__(self, **kwargs):
            for attribute, value in kwargs.items():
                setattr(self, attribute, value)
                
    >>> base_object = Base(**base_defaults)
    >>> base_object.memory_size
    >>> 8192
    >>> base_object.network_chunk_size
    >>> 4096
    
So we avoided, repeating ourselves, which is nice, but are there any other benefits
to doing things this way? Suppose we wanted to rename network_chunk_size to 
network_packet_size. In the first definition, we would have to change three
separate things, while in the second, we would only have to change one. This might
seem like only a minor convenience. However, the more things that need to be changed
the higher the probability that something will go wrong. With only a single class
definition the benefits are relatively small, but when our projects start to grow,
this will save a significant amount of time and headaches. 

This also enables our base object to accept arbitrary attributes simply be specifying
them as keyword arguments in the initialization call.

    >>> base_object = Base(testing=True)
    >>> base_object.testing
    >>> True
    
There is also another perk that might not be so immediately obvious. What if you wanted
to modify the default attributes/values that new instances are created with at runtime? 
In the first case, that would prove to be an ugly, relatively challenging mess. With our 
defaults dictionary it is a simple matter of changing the value and watching the results 
reflected in new instances.

We can actually take our defaults dictionary one step further. Previously we manually
supplied the dictionary to the call to instantiate the base object. It would be nice to
not have to do so. Python classes are themselves objects, which can have attributes. We
can attach our defaults dictionary to the class itself:

    class Base(object):
        
        defaults = base_defaults
        
        def __init__(self, **kwargs):
            options = self.defaults.copy()
            options.update(kwargs)
            self.attribute_setter(**options)
            
        def attribute_setter(self, **kwargs)
            for attribute, value in kwargs.items():
                setattr(self, attribute, value)
                
Note that because dictionaries are mutable datatypes, we make a copy of it so 
that when we update it with the keyword arguments supplied to the instance we
do not change the class defaults permanently. We also moved the attribute 
setting functionality outside of __init__ and into it's own method. It is a
wise investment to make things modular and therefore reusable. 

So now we know how to programmatically define attributes. It is also possible
to programmatically define classes in CPython. The built in type "type" is
actually what creates classes behind the scenes. The following produce the 
same results:

    class Attribute(Base):
        
        defaults = defaults.Attribute
        
        def __init__(self, **kwargs):
            super(Base, self).__init__(**kwargs)
            
    Attribute = type("Attribute", (Base, ), {"defaults" : defaults.Attribute})
    
The arguments supplied to type are the new class name, a tuple containing the
bases that the class inherits from, and a dictionary of attributes that will
become the class attributes. Assuming we have defined our Attribute class,
let's programmatically define some subclasses in the following example:

    # an rpg video game themed example
    attributes = ("Strength", "Endurance", "Dexterity", "Agility", "Intelligence", \
                  "Focus", "Wisdom", "Wits", "Cognition") 
                  
    for attribute in attributes:
        new_class = type(attribute, (Attribute, ), {})
    >>> Wits
    >>> <class 'base.Wits'>
    
We have just defined 9 new classes in 5 lines of code. It is not simply
convenient to have the computer write for you, the probability that at least
a single typo would have been made when manually writing out 9 different classes
is relatively high, even if you're a good typist. 