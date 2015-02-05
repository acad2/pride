Metapython
=========================
The short version
-------------------------

What is it?
  
    A python virtual machine that provides a structured environment where any number
    of arbitrarily complex logical processes can run concurrently. Processes
    can be paused/deleted, launched via other python modules, created at runtime from source, 
    and are scheduled to run according to their priority.
   
    Optional modules provide beginning support for low level audio manipulation, SDL2, 
    and compiled cython extensions may be avialable at some point in addition to the
    pure python version.
 
What features does it offer?
    
    1. Automatically generated documentation (docstrings and websites)
    2. Automatically generated command line argument parser
    3. Automatic verbosity handling 
     
    4. Effortless concurrency for nonblocking tasks. Processes are cooperatively
       scheduled and processed one frame at a time. Little reliance on global
       data structures makes locking mechanisms seldom needed. 
     
    5. An interactive interpreter that runs as process on the virtual machine. 
       Allows for remote login (but has a juvenile authentication scheme!). 
       The ability to execute Instruction objects and arbitrary python code via the interpreter
       allows for powerful process management. This includes the ability
       to update a running process without stopping or (potentially) even pausing it
     
     Objects that inherit from the Base object type have a number of builtin features:
     
     1. Abundant docstrings - even if the author neglected or declined to write one.
     2. Programmatic object instantiation via the create method, and explicit
        object deletion via the delete method
     3. Specify decorators and monkey patches via keyword argument to any method call.
     4. The simple message passing mechanisms send_to and read_messages can be used to
        send raw bytes to memory accessible by another process (physical or logical)
     5. The alert method, which allows assignment of verbosity level to messages.
        Messages are logged and/or printed according to message level and user settings.
        Alerts also provides callback method and callback Instruction options.
         
Where can I learn more?

    Investigate https://github.com/erose1337/Metaprogramming_Framework
  
What are the dependencies?
    
    Python 2.7 compatible
    - (optional) audio utilizes the PyAudio module, or pyalsaaudio on linux
    - (optional) gui utilizes pysdl2 and SDL2
    
The long version
===================
Start reading the tutorial at 