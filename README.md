Metaprogramming_Framework
=========================

all sorts of runtime fun in python

Q: What is it?
A: This is an application development framework. The tools contained within allow one to quickly and relatively easily
   develop applications that benefit from a variety of useful features.
   
   Some of these features include:
    Framework processes are automatically ran concurrently without threads, multiple physical processes, or even 
    coroutines. Traditional data locking mechanisms are seldom needed.
    
    Almost anything can be accomplished at runtime. This includes the ability define/create new processes or to 
    modify/extend/pause/delete existing ones.
    
    Useful docstrings - even if the author neglected or declined to write one.
    
    Specify decorators, context managers, and monkey patches via keyword argument to any method call. Very useful
    with the included Tracer decorator that gives the source for every line of code that was executed, and the
    Timed decorator for quick efficiency tests.
    
    A runtime interactive interprter. Allows you to play with all of the above concepts while your application(s) are
    running. Allows for remote login and has a very basic authentication scheme.
    
Q: What does it do?
A: Being moreso a set of tools then an application itself, the framework technically does not *do* anything. 
   Included are a few sample programs that tie together the framework in the way required to accomplish their need.
   
Q: Where can I learn more?
A: Right now, you'll have to open up the source and read it for yourself. A guide will be available whenever things reach
   a state of relative permanence. The source was written to be friendly to those reading it though, so don't be scared.
  
Q: What are the dependencies?
A: audiolibrary.py utilizes the PyAudio module. If you do not require audio you do not require this dependency.
   
