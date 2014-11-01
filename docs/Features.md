Virtual machine
-----------
An asynchronous pure python virtual machine that can run arbitrary separate processes 
within a single thread of execution. This is accomplished via an event stream instead
of a pipeline; There is a central nexus that Events flow to when submitted. Simply
posting an event for the handler to pick up queues up your instruction for processing.

If you have your own project that isn't at a fresh start but you would benefit from a 
particular functionality a virtual machine offers, you can embed a machine in your
standard python script simply by configuring and instantiating a machine and 
using a CPython thread to run it:
    
    from my_project import my_machine
    import threading
    thread = threading.Thread(target=my_machine.run)
    thread.start()
    ... your non framework code goes here ...

Developing your own Processes for a virtual machine is straightforward and takes a
similar form to the standard library Process/Thread interface:

    class Task_Scheduler(base.Process):
    
        defaults = defaults.Task_Scheduler
    
        def __init__(self, **kwargs):
            super(Task_Scheduler, self).__init__(**kwargs)
            self.objects["Timer"] = []
                
        def run(self):
            for timer in self.objects["Timer"]:
                timer.run()
                
            Event("Task_Scheduler0", "run", component=self).post()
                
Whatever is defined in the run method will be called once per frame. If you 
need the process to run more then one frame, it must be perpetuated via an event.


Framework Base object
-----------
base.py contains a class named Base. All framework objects descend from this class in a 
similar capacity as CPython objects all inherit from object. Objects that inherit from base
inherit a variety of features for working conveniently with the framework. What better place
to get information then the doc string?

    import base
    print base.Base.__doc__
    Base:
        A base object to inherit from. an object that inherits from base 
        can have arbitrary attributes set upon object instantiation by specifying 
        them as keyword arguments. An object that inherits from base will also 
        be able to create/hold arbitrary python objects by specifying them as 
        arguments to create.
    
        classes that inherit from base should specify a class.defaults dictionary that will automatically
        include the specified (attribute, value) pairs on all new instances

    Default values for newly created instances:
        memory_size	8096
        network_chunk_size	4096

    This object defines the following public methods:
        1. read_messages, which uses the following argument specification:
            Required arguments: ['self']
        2. get_family_tree, which uses the following argument specification:
            Required arguments: ['self']
        3. attribute_setter, which uses the following argument specification:
            Required arguments: ['self']
            Keyword arguments: kwargs
        4. warning, which uses the following argument specification:
            Required arguments: ['self', 'message', 'level', 'callback', 'callback_event']
            Default arguments: ('Error_Code', 'Warning', None, None)
        5. get_children, which uses the following argument specification:
            Required arguments: ['self']
        6. create, which uses the following argument specification:
            Required arguments: ['self', 'instance_type']
            Variable positional arguments: args
            Keyword arguments: kwargs
        7. send_to, which uses the following argument specification:
            Required arguments: ['self', 'component_name', 'message']
        8. add, which uses the following argument specification:
            Required arguments: ['self', 'instance']
        9. delete, which uses the following argument specification:
            Required arguments: ['self']
            Variable positional arguments: args

    This objects method resolution order/class hierarchy is:
        (<class 'base.Base'>, <type 'object'>)
        
Base objects automatically come pre supplied with abundant docstring information.
Parsing through this, we see the default values for new instances (more on those in 
a moment), and the public methods exposed by the object. Going through the methods, we
see the basic methods for interacting with the framework. The create, add, and delete 
methods automatically take care of instantiating/adding/deleting objects in a framework 
friendly way. The get_children and get_family_tree methods lookup all objects that
self has created/added with the previous methods. The warning method allows your component
to print messages to the screen. The send_to and read_messages methods are for sending
data to other components. The attribute_setter method sets the supplied keyword arguments
as attributes on the object. This method is called in Base.__init__

Let's return to those default attributes. A trivial example of a standard 
CPython class definition:
    
    class My_Class(object):
        
        def __init__(self, positional_arg, my_default=True, flags=None):
            self.my_default = my_default
            self.flags = flags
            if positional_arg == False:
                print "positional arg was False!"

    my_object = My_Class(False, flags=("a little bit of this", "a little bit of that"))
    "positional arg was False!"
    my_object.my_default
    >>> True
    my_object.flags
    >>> ("a little bit of this", "a little bit of that")
    
Rewriting this as a base object:
    
    import defaults
    # where defaults.My_Class = {"my_default" : True, "flags" : None}
    
    class My_Class(base.Base):
        
        defaults = defaults.My_Class
        
        def __init__(self, positional_arg, **kwargs):
            super(My_Class, self).__init__(**kwargs)
            if positional_arg = False:
                print "positional arg was False!"
     
    my_object = My_Class(False, flags=("a little bit of this", "a little bit of that"))
    "positional arg was False!"
    my_object.my_default
    >>> True
    my_object.flags
    >>> ("a little bit of this", "a little bit of that")           
    
Classes have a "defaults" attribute, which is a dictionary that contains the default 
attributes/values for new instances. Whatever is in the class defaults dictionary is 
automatically copied and updated with kwargs whenever a new instance is instantiated.

Having defaults stored as a class variable instead of hardcoded in __init__
and using the attribute_setter method provides a number of perks:

- eliminates the need to type the self.attribute = value statements that are omnipresent 
elsewhere in python. 
- less code to type means less time required and less room for human error
- makes such attributes modifiable at runtime
- automatically provides documentation

The attribute setter method relates to the central idea of the framework and computing in 
general: repetitive actions should be consigned to software functions instead of performed 
by humans. 


Automatic concurrency
-----------
The organized design of the project allows you to write single threaded/single process
components and have them run concurrently (as long as there's no blocking calls... for now!)
    
Data locks are seldom required because each component is localized to and only operates in 
it's own namespace. It would be uneconomic and ugly (though not impossible) to interact with 
other components data members. When one component needs access to anothers data, component A's 
data is packaged up and written to component B's memory for it to now have access to.

       
Runtime decoration, monkey patches, and context managers
-----------
Offers the ability to execute any individual method call with the supplied context manager,
decorator, decorators, or monkey patch via keyword argument. Argument names should a string 
of the module the patch or decorator resides in followed by the name of the patch/decorator itself. 
If the module name is not supplied, it is assumed to be "__main__".
    
Enables the syntax:

    object.method(monkey_patch="my_module.my_patch") 

    object.method(decorator="my_module.mydecorator")

    object.method(decorators=("my_module.mydecorator1", "my_module.mydecorator2"))
    
These calls do not modify the class or method in any way. The individual call itself is the
only thing that will function differently. 
    
Included for use with the above is a decoratorlibrary with various utilities.
Such utilities include:

- Tracer decorator that provides the source code of every line that is executed
- Timer decorator that provides the time taken to call a particular method
- Pystone_Test decorator that provides the number of pystones required to execute the method
- Argument logger
- Source code dump    

Of course, you may provide your own patches/decorators. You might even want to...
    
Define new classes/functions at runtime
---------
Included is an embedded python interpreter. This component lives at interpreter.Shell_Service.
It allows simultaneous remote connection to a virtual system and can manage the namespace for
each connected user. The shell client features non blocking input and can be used even locally 
in the same thread/process that your application is running in without interrupting it. 
   
This interpreter allows you to do the things that a regular live python interpreter session
would allow you to do. This includes things like defining new classes and functions at runtime. 
   
Given the previous section, it's probably obvious what you might want to define new functions for.
   
You may wonder what would be gained by defining a new class when your machine is already running?
   
Well, the event based design allows completely new processes to be started without even pausing the 
machine or any other processes running on it
   
The interpreter is also a convenient access point for updating running processes. Currently this 
functionality has been demonstrated in simple use cases, but will eventually lead to the options
to only patch the process in memory, commit the update to disk, and overwrite the old source with
the new update.
      
The interpreter is also makes a convenient command line interface. If all the power of python is
overwhelming for your admins, or you want a more specific/narrow range of commands, simply disable 
the builtins and expose only the functions/variables you want logged in clients to have access to.
   
Easy to read source
-----------
If you want to open things up and take a look at how things are working, or if you need to make
modifications for your own purposes, the source code is explicitly typed and written with the
intent of readability. Abbreviations are nowhere to be found - it should be abundantly clear what
is going on where.