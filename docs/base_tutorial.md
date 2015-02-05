Crash course
============

There is a root inheritance object named mpre.base.Base. Classes that inherit from Base
will inherit a number of convenient methods and features. The vmlibrary.Process 
class is a subclass of Base and is what you will often be working with.
Let's define some demonstartion Process classes:

    import mpre.vmlibrary as vmlibrary
    import mpre.defaults
    
    # a vmlibrary.Process runs on the virtual machine
    class Demo_ProcessA(vmlibrary.Process):
        
        # The attribute:value pairs in defaults are automatically 
        # assigned in Base.__init__ unless overriden via kwargs
        defaults = mpre.defaults.Process.copy()
        defaults.update({"flag_is_set" : False,
                         "data" : "Hello world from {}!"})
                         
        def __init__(self, **kwargs):
            # any keyword argument given a value will be automatically
            # assigned as an attribute to this object in super.__init__
            # (no need for self.x = x...)
            # The vmlibrary.Process class includes a default attribute
            # auto_start, which, when True, __init__ will automatically
            # enqueue the processes.run method via an Instruction
            
            super(Demo_Process, self).__init__(**kwargs)
            
        def run(self):            
            if self.flag_is_set:
                # the alert method will take the specified message
                # with the supplied iterable of str.format args,
                # and if the messages verbosity level is within
                # the specified range it will be printed and/or 
                # logged to disk. level=0 indicates an error
                
                self.alert("Inside {}.run, flag_is_set == True", 
                           [self.instance_name],
                           level='v')
            
            # send raw bytes to memory accessible by the Base object 
            # known as Demo_ProcessB
            
            self.send_to("Demo_ProcessB", "Hello from {}!".format(self))
            
            # queue the run instruction to be called 
            # again in self.priority seconds
            
            self.run_event.execute()
            
            
    class Demo_ProcessB(vmlibrary.Process):
        
        defaults = mpre.defaults.Process.copy()
        defaults.update({"check_for_messages" : True})
        
        def __init__(self, **kwargs):
            super(Demo_ProcessB, self).__init__(**kwargs)
            
        def run(self):
            if self.check_for_messages:
                self.alert("{} Checking for messages...", 
                           [self.instance_name],
                           level='v')
                           
                # read_messages accesses the memory chunk owned
                # by this object and returns an iterable of
                # whatever messages have been recieved. This is
                # the read counterpart of send_to
                
                messages = self.read_messages()
                if messages:
                    for message in messages:
                        self.alert(message, level='vv')
                        
                    # Let's imagine this was a condition that warranted program exit
                    # Instruction objects enqueue the processing of the specified
                    # base component and method. The call is not executed in this scope,
                    # but in the processors scope when it is time. The default Instruction
                    # priority is 0.0, which means schedule immediately (unit is in seconds)
                    
                    Instruction("Metapython", "exit").execute()
    
    # Here's the less preferred way to start a process
    # and a demonstration of attribute assignment via keyword argument
    
    demo_processa = Demo_ProcessA(auto_start=False)
    Instruction("System", "add", demo_processa).execute()
    
    # Here is the preferred way to start a process. This one Instruction
    # makes the System object instantiate a Demo_ProcessB object.
    # Because of the auto_start=True flag, the new process also starts running.
    
    Instruction("System", "create", Demo_ProcessB, parse_args=True).execute()
    
    # We can refer to any Base object from anywhere via Instructions by specifying
    # their instance_name as the first argument. An objects instance_name is a combination 
    # of it's class name and instance number. An objects instance_number is the count
    # of how many objects of that type have been instantiated so far. When the object is 
    # instance number 0 of it's class, it can be referred to without the 0. But if we started 
    # another Demo_ProcessA, that one would be Demo_ProcessA1 and would have to be referred
    # to as such.
    
    # The second required argument to an Instruction is the method that should be called
    # Instructions also accept *args and **kwargs to make them transparent with
    # regular method calls.
    
    Instruction("Demo_ProcessA", "run").execute()
                    
Base objects utilize a class.defaults dictionary. This dictionary contains
attribute:value pairs that will automatically be assigned to new instances
upon call to Base.\_\_init\_\_. Base objects accept any keyword arguments supplied
to the call to instantiate an object. Attributes specified this way will override
class default attributes.

vmlibrary.Process \_\_init\_\_ checks for a self.auto_start flag. If this flag is True,
an instruction is executed enqueueing the call to Process.start with the processor.
This flag is True by default and may be altered via class.defaults or
more commonly as keyword arguments in cases where such behavior is desired.

class.defaults also provide the information required for automatic command line
argument parsing. 

In our above example, Demo_ProcessA has the capability to accept --flag_is_set 
and --data from the command line. This behavior is activated when required 
via setting the keyword argument parse_args=True in the call to instantiate 
the object in question. If there are attributes in the class.defaults that
you do not want to be accessible via command line argument assignment, then
specify those attributes in an iterable named parser_ignore in your class definition.
If you desire short flags or positional arguments, then investigate the parser_modifiers
class attribute. For an example, let's look at the mpre.metapython.Metapython class::

    class Metapython(vmlibrary.Process):

    defaults = defaults.Metapython

    parser_ignore = ("environment_setup", "prompt", "copyright", "authentication_scheme",
                     "traceback", "memory_size", "network_packet_size", 
                     "interface", "port")
                     
    parser_modifiers = {"command" : {"types" : ("positional", ),
                                     "nargs" : '?'},
                        "help" : {"types" : ("short", "long"),
                                  "nargs" : '?'}
                        }
    exit_on_help = False
    # just the relevant segment

Many attributes in this particular scenario are ignored because they clutter up
the help list with pointless entries[1]_. 

In parser_modifiers, we have specified that the "command" argument should be
positional, and the "nargs" modifier is "?", which means this argument is
optional. The help command is made available with both -h and --help switches,
as specified by the types short and long. It too is marked as optional. The
exit_on_help flag determines whether or not to allow the propagation of SystemExit
from the underlying argparse parser after --help is encountered.

---------------
.. [1] This is also because metapython uses parse_args=True to retreive the 
       command/module to run, and the user likely intends their arguments to go 
       to that module and not metapython.