What is pride
------------
Pride stands for "python runtime and integrated development environment". 
Pride offers various python modules and a dynamic software environment that
aim to increase the rate at which complete, high quality applications can be 
produced. Using pride, you can develop concurrent, secure, multi-user ready
applications in a minimal amount of time.

Some application features that pride supports "out of the box" include:
    
    - User to User level communication
        - Forget tcp/ip network sockets!
        - Pride features a secure remote procedure call portal, with a data 
          transfer service built on top
            - Just register with the data transfer service and you can send
              data directly to any other registered users. 
                - All networking and security is handled elsewhere
        - A host proof data transfer service is being planned/developed
        
    - Effortless concurrency
        - "Regular" python does not feature indirection (aka references or "pointers")
        - All Base objects in pride have a reference
            - Similar to a well known name in dbus, if you're familiar
        - References are "dereferenced" via the pride.objects dictionary  
            - The dictionary keys are string references
            - The dictionary values the object that the string references
        - All operations take place in a single thread and may proceed as
          though they are atomic*
            - No mutexes, locks, semaphores, coroutines, or stack frame
              switches are required
        - Just grab the component you need from the objects dictionary
          when you need it, then let it fall out of scope
          
    - Base objects have an explicit destructor: the delete method
        - Guaranteed that object.delete() will garbage collect the object
            - As long as there's no references to the literal object, anyways!
            
    - Saving/loading 
        - Done securely, without pickle
        - Can be performed at arbitrary points of program execution
        
    - Updating
        - Components can be updated from source at runtime without restart
        
    - Easy to use crypto
        - User objects feature encrypt/decrypt methods
            - Always uses authenticated encryption
            - Fits the cannonical interface: ciphertext = user.encrypt(plaintext)
                - Returns a cryptogram; decryption is plaintext = user.decrypt(ciphertext)
                    - Cryptogram includes all information, such as iv and 
                      required algorithms
            - Support for unencrypted authenticated associated data
        
        - Or, even easier, encrypted database file objects:
            - Can read and write, and use as a context manager just like a normal file
                - Writes are buffered to memory and encrypted when the file is saved
                    - File is stored inside a database, and not directly in the file system
                        - Filenames can be obfuscated                            
        
    - Never waste time rolling another argument parser again!
        - Components can receive attributes from the command line, just by
          supplying parse_args=True to the objects initialization.
        - Supported attributes are determined by the objects default attributes        
        
    - Site config support
        - All objects can be customized to fit the needs of where they are
          deployed.
            - Any new default settings can be set here
        - Support for permanent entries
        - Support for single run entries via the command line with --site_config
        
    - Alpha support for graphical applications
        - Black box services run the application code on the server
            - The client simply sends keystrokes/clicks and receives 
              instructions for what to render to the screen    
        - All black box applications have multi user support by default
    
    - Simple logging and verbose output control
        - Simply supply your message and a level flag to the alert method
            - Try using Base objects verbosity dictionary to dispatch your level flags
                - Then you can modify them via the --site_config flag
                    - Good if you ever need to quickly up the level for debugging without
                      having to resort to editting the code.
        - Globally filter alert levels via the command line flag: --print_level
            - accepts args in the form: 0+v+vv+vvv+special_flag+....
                - Creates a set of flags that levels will be tested against
                - 0 represents errors and messages for the user
                    - Use 0 for things that should always be displayed
                - Incrementing quantities of 'v' indicate progressively 
                  verbose messages
                    - These are relative and assigned at your discretion
                - Special flags can be used for alerts you wish to single out
                    - Sometimes you just want one alert, and not a class of 
                      equally verbose messages
        - Similar to messages printed to stdout, there is a log_level flag
            - Functions exactly the same way as print_level, except that output
              goes to the alert handlers log file instead of stdout
            
    - Builtin command line interface
        - Allows you to explore and interact with your program while it runs
        - Due to the client server model everything runs on, this can be used 
          for convenient python style ssh for remote machine management
        - Supports python interpreter and os shell by default
        - Extensible with more programs
            - Including "Screensavers"!
          

Q: How is it licensed?
A: Pride is currently licensed under the GPL. If this ruined your day, let me
   know why and maybe we can figure something out.
  
Q: Where can I learn more?

A: Investigate https://github.com/erose1337/pride or jump straight into the documentation
   at http://erose1337.github.io/pride/
   Be warned, documentation is still under development! 
   If in doubt, read the source. 
   If still in doubt, email the author.
   
Q: What are the dependencies?
    
A: Python 2.7+ is required. 
   - The "cryptography" python package and Openssl are required, but...
        - There is a "dummy" crypto module for those with install permission issues
            - It's going to be pretty slow, relatively speaking
            - Strongly discouraged for production
            - Great if you just wanted to try it out
            
   Optional packages require additional dependencies:
   1. Low level audio support requires pyalsaaudio on linux or pyaudio otherwise
   2. SDL support requires SDL2.0 and pysdl2

Q: I made something with pride!
Q: I want to help develop pride!
Q: I can't get it to work!
Q: How do I do xyz? Can pride do xyz?

A: Tell me about it and I'll do my best to get back to you: erose1337@hotmail.com


*Technically, the framework uses a second thread for non blocking keyboard 
input. However, this is transparent, and users of prides api will not require 
or be aware of any threading.
   