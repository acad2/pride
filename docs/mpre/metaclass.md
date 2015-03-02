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

Metaclass
--------
 The metaclass for mpre.base.Base. This metaclass is responsible for
        applying instance tracking information to the class, a parser for
        the class, and wrapping the class methods in Runtime_Decorators.

Parser
--------
	Faciltates automatically generated command line parsers. Parser
	   instances are class attributes assigned by the Metaclass




This object defines the following non-private methods:


- **get_options**(self, argument_info):

		  No documentation available



- **get_arguments**(self, argument_info):

		  No documentation available


This objects method resolution order is:

(class 'mpre.metaclass.Parser', type 'object')


Runtime_Decorator
--------
	 Provides the ability to call a method with a decorator, decorators,
	or monkey patch specified via keyword argument. This decorator
	inherits from object and utilizes the Documented metaclass.
	
	usage: wrapped_method(my_argument, decorator="decorators.Tracer")




No non-private methods are defined

This objects method resolution order is:

(class 'mpre.metaclass.Runtime_Decorator', type 'object')
