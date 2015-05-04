mpre.userinput
==============



Thread
--------------

	A class that represents a thread of control.

    This class can be safely subclassed in a limited fashion.

    


Method resolution order: 

	(<class 'threading.Thread'>, <class 'threading._Verbose'>, <type 'object'>)

- **isAlive**(self):

		Return whether the thread is alive.

        This method returns True just before the run() method starts until just
        after the run() method terminates. The module function enumerate()
        returns a list of all alive threads.

        


- **setName**(self, name):

		No documentation available


- **setDaemon**(self, daemonic):

		No documentation available


- **isDaemon**(self):

		No documentation available


- **join**(self, timeout):

		Wait until the thread terminates.

        This blocks the calling thread until the thread whose join() method is
        called terminates -- either normally or through an unhandled exception
        or until the optional timeout occurs.

        When the timeout argument is present and not None, it should be a
        floating point number specifying a timeout for the operation in seconds
        (or fractions thereof). As join() always returns None, you must call
        isAlive() after join() to decide whether a timeout happened -- if the
        thread is still alive, the join() call timed out.

        When the timeout argument is not present or None, the operation will
        block until the thread terminates.

        A thread can be join()ed many times.

        join() raises a RuntimeError if an attempt is made to join the current
        thread as that would cause a deadlock. It is also an error to join() a
        thread before it has been started and attempts to do so raises the same
        exception.

        


- **start**(self):

		Start the thread's activity.

        It must be called at most once per thread object. It arranges for the
        object's run() method to be invoked in a separate thread of control.

        This method will raise a RuntimeError if called more than once on the
        same thread object.

        


- **getName**(self):

		No documentation available


- **run**(self):

		Method representing the thread's activity.

        You may override this method in a subclass. The standard run() method
        invokes the callable object passed to the object's constructor as the
        target argument, if any, with sequential and keyword arguments taken
        from the args and kwargs arguments, respectively.

        


- **isAlive**(self):

		Return whether the thread is alive.

        This method returns True just before the run() method starts until just
        after the run() method terminates. The module function enumerate()
        returns a list of all alive threads.

        


User_Input
--------------

	 Captures user input and provides the input to any listening component


Instance defaults: 

	{'_deleted': False,
	 'auto_start': True,
	 'priority': 0.04,
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.userinput.User_Input'>,
	 <class 'mpre.vmlibrary.Process'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

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


- **get_selection**(prompt, answers):

		No documentation available


- **get_user_input**(prompt):

		No documentation available


- **is_affirmative**(input):

		No documentation available
