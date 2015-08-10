Metaclass features
==================

The features in this category are provided by mpre.base.Metaclass. This metaclass is used
by mpre.base.Base, and is itself a subtype of the Documented type. 

Automatic Documentation
-----------------
The Documented metaclass replaces new class \_\_doc\_\_ attributes with a Docstring descriptor
object. This object returns a verbose documentation string. The string is a combination of any
original docstring with information about any class defaults, any non private methods
with their argument signatures and any docstrings found.

As a note, the mpre.package.Documentation object builds on these mechanisms. It produces .md 
files from the docstring provided by the Docstring descriptor, and runs mkdocs to generate
a documentation website. Much of this website was generated this way.

Runtime Decoration
------------------

Methods of base objects are automatically wrapped in a Runtime_Decorator. This decorator
parses keyword arguments for the terms "decorator", "decorators", and "monkey_patch". 

    - The decorator argument is a string module path that points to a decorator type or function.
    - The decorators argument is an iterable of string module paths as above
    - The monkey_patch argument takes string module path to a replacement method

If any are provided, they will be applied to the original wrapped method and the resulting function
called. If none are provided, the original wrapped function is called without modification.

    >>> def monkey_patch(self, *args, **kwargs):
    >>>     print "And now for something completely different"
    >>>     
    >>> b = mpre.base.Base()
    
    >>> # local replacements are referred to without a modulename prefix
    >>> b.create("socket.socket", monkey_patch="monkey_patch")
    >>> And now for something completely different
    
Command line parsers
--------------------
The metaclass examines each class defaults dictionary that it finds and creates a parser for that
class. If the argument parse_args=True is passed to the constructor of a Base object, this
parser will be used to interpret command line arguments as attributes for the new instance.
Only arguments listed in the class defaults dictionary will be used. Arguments set this way
override any conflicting keyword arguments specified to the constructor.
    
This is particularly useful with the verbosity attribute and alerts.

