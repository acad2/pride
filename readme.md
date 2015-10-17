Pride
=========================
Python Runtime and Integrated Development Environment

Q: What is it?

A: An application framework. Programs written with pride tend to be very concise
   yet very capable.
    
Q: What features does it offer?

A: Most features are aimed at productivity and an improving minimum standard of quality.
   1. Automatically generated documentation (docstrings and websites) - zero config
   2. Automatically generated command line argument parsers - zero config
   3. Automatic verbosity handling and logging 
   4. Simple mutex free concurrency 
   5. Objects can be updated from source at runtime without pausing or stopping execution
   6. Application state can be saved/loaded
   7. A concurrent interactive shell that reduces/eliminates the need for a debugger
   8. Simple, secure remote procedure calls with authenticated clients/servers. 
      remote object access requires zero config, aside from username/password setup.
   
Q: Where can I learn more?

A: Investigate https://github.com/erose1337/pride or jump straight into the documentation
   at http://erose1337.github.io/pride/
  
Q: What are the dependencies?
    
A: Python 2.7+ is required. optional modules require additional dependencies:
   1. Low level audio support requires pyalsaaudio on linux or pyaudio otherwise
   2. SDL support requires SDL2.0 and pysdl2