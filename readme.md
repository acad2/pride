Pride
=========================
Python Runtime and Integrated Development Environment

Q: What is it?

A: An application framework. Programs written with pride tend to be very concise
   yet very capable. Since portions of the program are created programmatically,
   programs written with pride potentially have less bugs and are easier to
   maintain then an equivalent python program written solely by a human hand.
    
Q: What features does it offer?

A: Available modules range deal with subjects ranging from:
    
   - manipulating source code before compilation (a.k.a preprocessing or macros)
   - developing secure network services
   - working with low level audio
   - working with graphics (SDL2)
   
   Programs written with pride automatically have the following qualities:
   
   - Verbose documentation strings
   - Command line argument parser
   - Output verbosity/logging according to user specified levels
   - Update-able from source code at runtime, without stopping or restarting
   
   Features offered by the environment and objects that reside in it include:
   
   - Simple, mutex free concurrency
   - Network services are completely decoupled from networking via secure RPC
   - A concurrent python command line that can be used to monitor/debug program
     status or as a general purpose command line shell.
   - Database objects with an api that requires little knowledge of SQL (Sqlite3 backend)
   - Virtual file system that supports encrypted + non indexable files
   - Extensible macro/preprocessor support
   - Various wrappers, adapters, and patching tools, for converting preexisting
     modules and objects. Wrapper objects bestow pride Base object functionality
     onto arbitrary python objects.
     
   Various less developed features include:
   
   - Automatically generated documentation websites (via mkdocs)
   - Static compilation via Cython, can create real binary exe/dll/so/pyd 
   
Q: Where can I learn more?

A: Investigate https://github.com/erose1337/pride or jump straight into the documentation
   at http://erose1337.github.io/pride/
  
Q: What are the dependencies?
    
A: Python 2.7+ is required. The cryptography package is required.
   Optional packages require optional dependencies:
   1. Low level audio support requires pyalsaaudio on linux or pyaudio otherwise
   2. SDL support requires SDL2.0 and pysdl2
   3. Documentation websites require mkdocs
   4. Static compilation requires Cython and a compiler