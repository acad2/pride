dialect
==============



Dialect
--------------

	 usage: dialect = Dialect(dictionary) # create a dialect which switches keys for values
        modified_input = dialect.translate(input) # perform the translation on text string
        original_input = dialect.translate(modified_input, "from") # reverse a translation


Method resolution order: 

	(<class 'dialect.Dialect'>, <type 'object'>)

- **translate_from**(self, _file):

				No documentation available


- **translate_to_file**(self, input_file, output_file):

				No documentation available


- **translate**(self, _file):

				No documentation available


- **save**(self, filename, mode):

				No documentation available


- **from_object**(self, object):

				No documentation available


StringIO
--------------

**StringIO**:

		class StringIO([buffer])

    When a StringIO object is created, it can be initialized to an existing
    string by passing the string to the constructor. If no string is given,
    the StringIO will start empty.

    The StringIO object can accept either Unicode or 8-bit strings, but
    mixing the two may take some care. If both are used, 8-bit strings that
    cannot be interpreted as 7-bit ASCII (that use the 8th bit) will cause
    a UnicodeError to be raised when getvalue() is called.
    


randint
--------------

**randint**(self, a, b):

		Return random integer in range [a, b], including both end points.
        
