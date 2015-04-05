mpre.metaclass
========
No documentation available

Docstring
--------
 A descriptor object used by the Documented metaclass. Augments
        instance docstrings with introspected information

Documented
--------
 A metaclass that uses the Docstring object to supply
        abundant documentation for classes

Instance_Tracker
--------
 Provides instance tracking and counting attributes.
    
        Note as of 3/3/2015: the class must implement these attributes,
        it is not performed by this metaclass

Metaclass
--------
 A metaclass that applies other metaclasses. Each metaclass
        in the list Metaclass.metaclasses will be chained into a 
        new single inheritance metaclass that utilizes each entry. 
        The methods insert_metaclass and remove_metaclass may be used
        to alter the contents of this list.
        
        Implementation currently under examination due to compiling with
        cython being broken

Method_Hook
--------
 Provides a hook on all methods for the new class. This metaclass
        uses this hook to wrap each method in a Runtime_Decorator.

Parser
--------
	 Faciltates automatically generated command line parsers. Parser
	instances are class attributes assigned by the Parser_Metaclass




This object defines the following non-private methods:


- **get_options**(self, argument_info):

		  No documentation available



- **get_arguments**(self, argument_info):

		  No documentation available


This objects method resolution order is:

(class 'mpre.metaclass.Parser', type 'object')


Parser_Metaclass
--------
 Provides a command line parser for a class based upon 
        the class.defaults dictionary

Runtime_Decorator
--------
	 Provides the ability to call a method with a decorator, decorators,
	or monkey patch specified via keyword argument. This decorator
	inherits from object and utilizes the Documented metaclass.
	
	usage: wrapped_method(my_argument, decorator="decorators.Tracer")




No non-private methods are defined

This objects method resolution order is:

(class 'mpre.metaclass.Runtime_Decorator', type 'object')
