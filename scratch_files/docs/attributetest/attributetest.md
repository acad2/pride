attributetest
==============



Persistent_Reactor
--------------

No docstring found


Struct
--------------

No documentation available


- **create_struct(self, dictionary):

		No documentation available


- **create_metadata(self, attribute_order, byte_offsets, is_pickled):

		 create a metadata struct that provides attribute names,
            the pickled flag, and the associated offset/size.


- **byte_representation(self, dictionary):

		No documentation available


- **update(self, dictionary):

		No documentation available


- **from_dictionary(self, dictionary):

		No documentation available


- **pack(self, value):

		No documentation available


izip
--------------

izip(iter1 [,iter2 [...]]) --> izip object
		
		Return a izip object whose .next() method returns a tuple where
		the i-th element comes from the i-th iterable argument.  The .next()
		method continues until the shortest iterable in the argument sequence
		is exhausted and then it raises StopIteration.  Works like the zip()
		function but consumes less memory by returning an iterator instead of
		a list.
