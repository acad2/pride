mpre.userinput
========
No documentation available

Thread
--------
A class that represents a thread of control.

    This class can be safely subclassed in a limited fashion.

    

User_Input
--------
	 Captures user input and provides the input to any listening component

Default values for newly created instances:

- priority                 : 0.04
- memory_size              : 4096
- memory_mode              : -1
- auto_start               : True
- deleted                  : False
- verbosity                : 

This object defines the following non-private methods:


- **add_listener**(self, sender, argument):

		  Adds a component to listeners. Components added this way should support a    
		 handle_keystrokes method



- **run**(self):

		  No documentation available



- **read_input**(self):

		  No documentation available



- **on_load**(self, attributes):

		  No documentation available



- **remove_listener**(self, sender, argument):

		  No documentation available


This objects method resolution order is:

(class 'mpre.userinput.User_Input', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')
