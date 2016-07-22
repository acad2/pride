pride.decorators
==============



Dump_Source
--------------

	Tracer decorator that dumps source code to disk instead of writing to sys.stdout.


Method resolution order: 

	(<class 'pride.decorators.Dump_Source'>,
	 <class 'pride.decorators.Tracer'>,
	 <type 'object'>)

Pystone_Test
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.decorators.Pystone_Test'>, <type 'object'>)

Timed
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.decorators.Timed'>, <type 'object'>)

Tracer
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.decorators.Tracer'>, <type 'object'>)

- **trace**(self, frame, instruction, arg):

				No documentation available


- **get_frame_info**(self, frame):

				No documentation available


call_if
--------------

**call_if**(conditions):

				No documentation available


enter
--------------

**enter**(enter_function):

				No documentation available


exit
--------------

**exit**(exit_function):

				No documentation available


on_exception
--------------

**on_exception**(exception, callback):

				No documentation available


required_arguments
--------------

**required_arguments**(no_args, no_kwargs, requires_args, requires_kwargs, **_kwargs):

				No documentation available


with_arguments_from
--------------

**with_arguments_from**(entry_function):

				No documentation available


wraps
--------------

**wraps**(wrapped, assigned, updated):

		Decorator factory to apply update_wrapper() to a wrapper function

       Returns a decorator that invokes update_wrapper() with the decorated
       function as the wrapper argument and the arguments to wraps() as the
       remaining arguments. Default arguments are as for update_wrapper().
       This is a convenience function to simplify applying partial() to
       update_wrapper().
    
