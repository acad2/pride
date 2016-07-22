pride
==============

 Stores global objects including instructions, the alert handler, and the finalizer 

Alert_Handler
--------------

	 Provides the backend for the base.alert method. The print_level
        and log_level attributes act as global levels for alerts;
        print_level and log_level may be specified as command line arguments
        upon program startup to globally control verbosity/logging. 


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'log_is_persistent': False,
	 'log_level': '0+v',
	 'log_name': 'c:\\users\\_\\pythonbs\\pride\\Alerts.log',
	 'parse_args': True,
	 'print_level': '0',
	 'replace_reference_on_load': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.Alert_Handler'>, <class 'pride.base.Base'>, <type 'object'>)

- **dump_log**(self, byte_count, lines):

				No documentation available


Finalizer
--------------

	No docstring found


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'replace_reference_on_load': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.Finalizer'>, <class 'pride.base.Base'>, <type 'object'>)

- **run**(self):

				No documentation available


- **remove_callback**(self, callback, *args, **kwargs):

				No documentation available


- **add_callback**(self, callback, *args, **kwargs):

				No documentation available


Instruction
--------------

	 usage: Instruction(component_name, method_name,
                           *args, **kwargs).execute(priority=priority,
                                                    callback=callback)

            - component_name is the string reference of the component
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.


        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will be performed. Instructions are useful for explicitly
        timed/recurring tasks.

        Instructions may be reused. The same instruction object can be
        executed any number of times.

        Note that Instructions must be executed to have any effect, and
        that they do not happen inline even if the priority is 0.0. In
        order to access the result of the executed function, a callback
        function can be provided.


Method resolution order: 

	(<class 'pride.Instruction'>, <type 'object'>)

- **execute**(self, priority, callback):

		 usage: instruction.execute(priority=0.0, callback=None)

            Submits an instruction to the processing queue.
            The instruction will be executed in priority seconds.
            An optional callback function can be provided if the return value
            of the instruction is needed. 


- **purge**(cls, reference):

				No documentation available


- **unschedule**(self):

				No documentation available


preprocess
--------------

**preprocess**(function):

				No documentation available
