Python Metaprogramming Framework
========

The python metaprogramming framework aspires to enable effortless, expeditious
software development. Paint a big picture quickly with good organization!

Utilizing a pure python virtual machine and the framework api for it, an end 
user can tie together a program and launch a machine in just a few lines of code:

    import machinelibrary
    import defaults
    from default_processes import *
    from base import Event

    defaults.System["startup_processes"] += (AUDIO_MANAGER, )
    machine = machinelibrary.Machine()
    Event("Audio_Manager0", "play_wav_file", "test_wav.wav").post()

    if __name__ == "__main__":
        machine.run()

Features
--------
A small slice of what all is available:

- Concurrency for vm processes is managed automatically and performed in serial within a 
single physical thread/process.
    
- Fully object oriented design combines with a simple messaging scheme to makes global variables 
and locking mechanisms seldom needed.
    
- Almost anything can be accomplished at runtime. This includes the ability define/create 
new processes and to modify/extend/pause/delete existing ones.
 
- Specify decorators, context managers, and monkey patches via keyword argument to any individual method call. 

- Useful docstrings, even if the author neglected or declined to write one.

- A runtime interactive interprter. Allows you to play with all of the above concepts while your 
application(s) are running. Allows for remote login which provides a ready to go, customizable 
command line interface for your application(s) or server(s).

Installation
------------

Install the metaprogramming framework by downloading the zip from github:

- https://github.com/erose1337/Metaprogramming_Framework/archive/master.zip
- pip setup.py install coming soon

Contribute
----------

- Issue Tracker: https://github.com/erose1337/Metaprogramming_Framework/issues
- Source Code: https://github.com/erose1337/Metaprogramming_Framework

Support
-------

If you are having issues, please let me know. I can be reached at erose1337@hotmail.com.
The project is currently in development.

Development and recipes can found at http://ellasawrus-rex.tumblr.com/

License
-------

The project is licensed under the GNU license.

Dependencies
-------

This project utilizes Python 2.7. External dependencies may be required depending on intended use:
   
- Currently: (optional) audiolibrary.py utilizes the PyAudio module, or pyalsaaudio on linux
   
- Future/Expected: (optional) pysdl2 - reintroduction of display/graphical applications

- Future/Possibly: (optional) dill - introduction of distributed computing, depends on pickleability of framework objects
   
- Previously: pygame - pre-machine layer graphical applications
