Metapython
=========================

all sorts of runtime fun in python

Q: What is it?
A:  A python virtual machine that provides a structured environment where any number
    of arbitrarily complex logical processes can be run concurrently. Processes
    can be paused/deleted, launched via other python modules, created at runtime from source, and are scheduled to run at specific intervals according to their priority.
    
    Optional modules provide beginning support for low level audio manipulation, SDL2, 
    and compiled cython extensions may be avialable at some point in addition to the
    pure python version that will always be available.
 
Q: What features does it offer?
A: A slice of what is available:
    Effortless concurrency for nonblocking tasks. Processes are cooperatively
    scheduled and designed to process one frame at a time. No reliance on global
    data structures eliminates any need for locking mechanisms. 
    
    An interactive interpreter that runs as process on the virtual machine. 
    Allows for remote login (but has a juvenile authentication scheme!). 
    The ability to execute Instruction objects and arbitrary python code via the interpreter allows for powerful process management. This includes the ability
    to update a running process without stopping or (potentially) even pausing it
    
    Objects that inherit from the Base object type have a number of builtins:
    
    1. Abundant docstrings - even if the author neglected or declined to write one.
    2. Programming object instantiation via the create method, and explicit
       object deletion via the delete method
    3. They can specify decorators and monkey patches via keyword argument to any 
       method call.
    4. The message passing mechanisms send_to and read_messages can be used to
       send raw bytes to memory owned by another process
    5. The alert method, which allows assignment of verbosity level to messages
       which can be used to determine whether or not to print or log said messages.
       It also provides callback method and callback Instruction options.
       
    
Q: Where can I learn more?
A: Investigate https://github.com/erose1337/Metaprogramming_Framework
  
Q: What are the dependencies?
A: Python 2.7 and:
   Currently:
    audiolibrary.py utilizes the PyAudio module, or pyalsaaudio on linux (optional module)
    sdllibrary utilizes pysdl2 and SDL2 (optional module)
    
