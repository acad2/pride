reference types - different ways of referencing

 - the current way. absolute, global lookup. Different classes that share the 
   same name will silently remove the ability to reference the first 
   insantiated object. Works nicely with preprocessor and the $ sign.
   
  - relative name lookup. implementation already proposed. Allows resolution
    of supplied path name, which is a string of instance names joined by
    '.' symbols. The first, leftmost name is the parent object. This object
    does not necessarily need a root parent object. It can be any object
    that has an instance name. The next instance name is a child object of
    the parent in question, and the instance after that a child object of that
    instance and so forth. 
    
    An important point to consider is how instance numbers are calculated. 
    For example, the string "Python.Network.Socket4" will go to the 
    Python object, go to the Network key, and get the 0th object from 
    that container. Next it goes to Network.objects and the Socket key and
    gets the object at the 4th index in the container. This socket is not
    necessarily the owner of the instance name Socket4; It was just the 
    object at the 4th index in the container.
    
    Could be made to work with absolute (real) instance names by mapping
    the instances name to it's position in the objects dictionary.
    
    Two instances of the same name would at least be referencable by 
    specifying their relative location.
    
    Unfortunately not a single solution. Doesn't prevent name collisions in
    the objects dictionary. Could maybe store the actual names in relative
    structure.
    
   - private instance names. Maybe use a memory address or hash. Would require
    a function call to acquire the reference. The instance name could not be 
    known ahead of time. 
        
        - how to request the reference. If you don't have a reference, how do
          you request the instance name?
        - how to determine whether or not to provide the reference 
        