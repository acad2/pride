Metapython
=========================

A dynamic runtime environment for python

Q: What is it?

A: A pacakge that provides various features aimed at increasing productivity and
   speed of development for those seeking to write applications in python. Features
   are mostly implemented via subclassing from an alternative base class
   then pythons built in object class. 
    
Q: What features does it offer?

A: Most features are aimed at productivity and improving the minimum standard for quality:
   1. Automatically generated documentation (docstrings and websites)
   2. Automatically generated command line argument parser
   3. Automatic verbosity handling and logging 
   4. Simple concurrency mechanisms which seldom require locking primitives of any kind 
   5. The ability to be updated from source at runtime without pausing or stopping execution
   6. The ability to take snapshots of application state, and restore snapshots at any point
   7. An interactive interpreter usable from your application (or remotely if enabled)
   
Q: Where can I learn more?

A: Investigate https://github.com/erose1337/Metapython or jump straight into the documentation
   at http://erose1337.github.io/Metapython/
  
Q: What are the dependencies?
    
A: Python 2.7+ is required. optional modules require additional dependencies:
   1. Low level audio support requires pyalsaaudio on linux or pyaudio otherwise
   2. SDL support requires SDL2.0 and pysdl2