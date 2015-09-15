Alerts explained
----------------
Base objects come equipped with an "alert" method. This method is generally
used in place of the print keyword/function for displaying application info
to users via sys.stdout. The objects instance name will be prepended to the
message automatically.
 
An alert takes 3 arguments: 
    
    - the string message to be printed
    - optionally, the arguments for string formatting for the string (if any)
    - optionally, the level of the alert, a value between 0, 'v', 'vv', 'vvv', ...,
      where more 'v' symbols means a more verbose message. 
      
The reason string format arguments can be supplied as an argument is for 
readability and laziness purposes. With a long message string, calling the
.format method may cause a line to run on excessively long. The following two
are equivalent:
    
    class Test(mpre.base.Base):
        
        defaults = mpre.base.Base.defaults.copy()
        defaults.update({"test_attribute" : True,
                         "test2" : 2})
        
        def __init__(self, **kwargs):
            super(Test, self).__init__(**kwargs)
            self.alert("Initialized, value of test_attribute: {}, test2: {}".format(self.test_attribute, 
                                                                                    self.test2),
                                                                                    level='vv')
                                                                                    
                                                                                    
    class Test(mpre.base.Base):
        
        defaults = mpre.base.Base.defaults.copy()
        defaults.update({"test_attribute" : True,
                         "test2" : 2})
        
        def __init__(self, **kwargs):
            super(Test, self).__init__(**kwargs)
            self.alert("Initialized, value of test_attribute: {}, test2: {}",
                       (self.test_attribute, self.test2), level='vv')
                       
                       
The second definition is more compact then the first. This could also be 
achieved by formatting the string before calling the alert method. However,
the alert method still has an advantage over that: laziness. Because the 
format does not happen unless the message would be printed/logged,
more verbose messages will be ignored and the format operation skipped.
Considering that more verbose messages could include copious amounts of data,
and many components exist simultaneously that all use alerts, it is polite to
save the cycles where possible.

Alerts also serve as self documenting code. They tend to make it very clear
what happens where, and their output is of great assistance when debugging. 

Alerts may be logged to disk. This can be controlled via the Alert_Handler
log_level attribute. A higher log_level will log more verbose messages to disk.
A log_level of -1 will not log anything to disk.

There is also a print_level attribute on the alert handler object. A higher
print_level will print more verbose messages to the screen. Setting it to -1
will silence all normal alerts. 

The print_level and log_level attributes can be passed in as command line
arguments when starting the program.