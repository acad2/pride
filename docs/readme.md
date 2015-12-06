Pride
=========================
Python Runtime and Integrated Development Environment

Q: What is it?

A: An application framework for the python programming language. Programs 
   written with pride tend to be concise, robust, capable, and extensible;
   all while remaining as simple and straightforward as possible.
    
Q: What features does it offer?

A: Most features are aimed at productivity and an improving minimum standard of quality.
   1. Automatically generated documentation (docstrings and websites)
   2. Automatically generated command line argument parsers for all Base objects
   3. Automatic verbosity handling and logging 
   4. Simple, headache free, mutex free concurrency 
   5. Objects can be updated from source at runtime without pausing or stopping execution
   6. Application state can be saved/loaded at arbitrary points of execution
   7. Simple, secure remote procedure calls with authenticated clients/servers. 
      Remote object access requires zero config, aside from basic security setup.
      Client/server applications can be developed without regard to sockets and
      network protocols with exclusive focus on application specific logic.
   8. A secure, concurrent interactive shell that reduces the need for a debugger.
      The secure rpc model mentioned above facilitates a python ssh-style command 
      line that be used to interact with and manage remote machines.      
      
Q: Where can I learn more?

A: Investigate https://github.com/erose1337/pride or jump straight into the documentation
   at http://erose1337.github.io/pride/
  
Q: What are the dependencies?
    
A: Python 2.7+ is required. The "cryptography" python package and Openssl are required.
   Optional packages require additional dependencies:
   1. Low level audio support requires pyalsaaudio on linux or pyaudio otherwise
   2. SDL support requires SDL2.0 and pysdl2
