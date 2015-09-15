Features
===============
Concurrency
---------------
Concurrency is facilitated by instance names, which provide a programmatic
reference to any component regardless of the current lexical scope. This
reference is somewhat similar to a C pointer, in that it is "dereferenced"
(looked up in a dictionary) and the actual object it refers to is returned.
They differ in that a pointer is usually a more or less random memory address
, while an instance name can be known before compiling and specified explicitly
in the source.

All objects that inherit from mpre.base.Base will have an instance name. 
It is located as the "instance_name" attribute of the object.
Objects that do not inherit from Base can acquire an instance name by being
instantiated via the create method instead of directly by calling the class
constructor. An object so created can acquire it's instance name by
supplying it's self as the key to mpre.environment.instance_name.

An instance name can be calculated and need not be memorized. The name is 
equal to the class name of the object, appended with the number of such
objects created so far (if any).

Looking up a name in the objects dictionary is such a common idiom that there
is a macro for making doing so more concise: the $ symbol. What immediately
follows the symbol is regarded as the instance name. Thus, the following two
examples are equivalent:
    
    def test():
        mpre.objects["Shell"].handle_input("print 'Hello world'")
        
    def test2():
        $Shell.handle_input("print 'Hello world'")
        
At compile time, source is preprocessed and any $ symbols are replaced and
expanded to the full lookup in mpre.objects. After preprocessing, the source
code from test2 is identical to the source code from test.

In the CPython documentation it is stated that '$' is not used by the 
interpreter. Hopefully there will be no conflicts.

This approach can be signficantly more concise and readable then some of the
alternatives. It is also very light weight and carries minimal overhead.

Instance names also facilitate distributed concurrency. For more information,
see "authentication".

optimizations:
----------------
    - generally applicable:
        
        - 
        
    - networking
        - nonblocking I/O - sends occur immediately, recvs are batch processed
        - network.Socket object send/recv between local endpoints happens inline
        - network.Socket send/recv uses the buffer interface with memoryviews and bytearrays
        - efficient non blocking connect that uses set intersections/differences
        - i/o buffers managed by application; can support very large buffer sizes
        
    - sdl renderer:
        - gui.window_object textures are cached and draw operations batch processed
        - texture layers (all textures of a given z coordinate) are cached
        - only invalidated layers are redrawn
        - scales well with large numbers of static window objects
        
Other
-------------------
Terminal "screensaver"
    