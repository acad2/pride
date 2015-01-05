Metapython
=========================

all sorts of runtime fun in python

Q: What is it?
A:  An embeddable python virtual machine capable of performing arbitrary separate processes in a
    single physical thread and process.
    
    Also, a development framework and api for writing programs for the aforementioned virtual machine.
 
Q: What features does it offer?
A: A small slice of what all is available:
    Fully object oriented design makes global variables and locking mechanisms seldom needed.
    
    Almost anything can be accomplished at runtime. This includes the ability define/create 
    new processes and to modify/extend/pause/delete existing ones.
 
    Specify decorators, context managers, and monkey patches via keyword argument to any method call. 
    Particularly useful with the included debug Tracing/Timing decorators.
    
    A runtime interactive interprter. Allows you to play with all of the above concepts while your 
    application(s) are running. Allows for remote login and has a very basic authentication scheme. 
    Provides a ready to go, customizable command line interface for your application(s) or server(s)
    
    Useful docstrings - even if the author neglected or declined to write one.
    
Q: Where can I learn more?
A: Investigate https://github.com/erose1337/Metaprogramming_Framework
  
Q: What are the dependencies?
A: Python 2.7 and:
   Currently:
    audiolibrary.py utilizes the PyAudio module, or pyalsaaudio on linux (optional)
   Future/Expected:
    pysdl2 - reintroduction of display/graphical applications (optional)
   Future/Possibly:
    dill - introduction of distributed computing, depending on pickle-ability of framework objects (optional)
   Previously:
    pygame - pre-machine layer graphical applications