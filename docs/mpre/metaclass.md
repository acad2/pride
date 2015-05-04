mpre.metaclass
==============



Docstring
--------------

	 A descriptor object used by the Documented metaclass. Augments
        instance docstrings with introspected information


Method resolution order: 

	(<class 'mpre.metaclass.Docstring'>, <type 'object'>)

Documented
--------------

	 A metaclass that uses the Docstring object to supply
        abundant documentation for classes


Method resolution order: 

	(<class 'mpre.metaclass.Documented'>, <type 'type'>, <type 'object'>)

Instance_Tracker
--------------

	 Provides instance tracking and counting attributes.
    
        Note as of 3/3/2015: the class must implement these attributes,
        it is not performed by this metaclass


Method resolution order: 

	(<class 'mpre.metaclass.Instance_Tracker'>, <type 'type'>, <type 'object'>)

Metaclass
--------------

	 A metaclass that applies other metaclasses. Each metaclass
        in the list Metaclass.metaclasses will be chained into a 
        new single inheritance metaclass that utilizes each entry. 
        The methods insert_metaclass and remove_metaclass may be used
        to alter the contents of this list.
        
        Implementation currently under examination due to compiling with
        cython being broken


Method resolution order: 

	(<class 'mpre.metaclass.Metaclass'>,
	 <class 'mpre.metaclass.Documented'>,
	 <class 'mpre.metaclass.Instance_Tracker'>,
	 <class 'mpre.metaclass.Parser_Metaclass'>,
	 <class 'mpre.metaclass.Method_Hook'>,
	 <type 'type'>,
	 <type 'object'>)

- **remove_metaclass**(cls, metaclass):

		No documentation available


- **update_metaclass**(cls):

		No documentation available


- **insert_metaclass**(cls, metaclass, index):

		No documentation available


Method_Hook
--------------

	 Provides a hook on all methods for the new class. This metaclass
        uses this hook to wrap each method in a Runtime_Decorator.


Method resolution order: 

	(<class 'mpre.metaclass.Method_Hook'>, <type 'type'>, <type 'object'>)

Parser
--------------

	 Faciltates automatically generated command line parsers. Parser
        instances are class attributes assigned by the Parser_Metaclass


Method resolution order: 

	(<class 'mpre.metaclass.Parser'>, <type 'object'>)

- **get_options**(self, argument_info):

		No documentation available


- **get_arguments**(self, argument_info):

		No documentation available


Parser_Metaclass
--------------

	 Provides a command line parser for a class based upon 
        the class.defaults dictionary


Method resolution order: 

	(<class 'mpre.metaclass.Parser_Metaclass'>, <type 'type'>, <type 'object'>)

Runtime_Decorator
--------------

	 Provides the ability to call a method with a decorator, decorators,
        or monkey patch specified via keyword argument. This decorator
        inherits from object and utilizes the Documented metaclass.

        usage: wrapped_method(my_argument, decorator="decorators.Tracer")


Method resolution order: 

	(<class 'mpre.metaclass.Runtime_Decorator'>, <type 'object'>)

- **copy**(x):

		Shallow copy operation on arbitrary Python objects.

    See the module's __doc__ string for more info.
    
