mpre.encrypt_test
==============



- **convert**(bytes, message_key, public_key):

		No documentation available


- **decrypt**(encrypted_message, public_key, message_key):

		No documentation available


- **derive_message_key**(message):

		No documentation available


- **derive_password_key**(public_key, password, hash_function, key_size):

		No documentation available


- **derive_public_key**(key_size, random_selection_size):

		No documentation available


- **derive_public_key512**(key_size, random_selection_size):

		No documentation available


- **encrypt**(message, public_key):

		No documentation available


- **grouper**(n, iterable, padvalue):

		grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')


izip_longest
--------------

	izip_longest(iter1 [,iter2 [...]], [fillvalue=None]) --> izip_longest object

Return an izip_longest object whose .next() method returns a tuple where
the i-th element comes from the i-th iterable argument.  The .next()
method continues until the longest iterable in the argument sequence
is exhausted and then it raises StopIteration.  When the shorter iterables
are exhausted, the fillvalue is substituted in their place.  The fillvalue
defaults to None or can be specified by a keyword argument.



Method resolution order: 

	(<type 'itertools.izip_longest'>, <type 'object'>)

- **next****:

		x.next() -> the next value, or raise StopIteration


- **test_convert**(message):

		No documentation available


- **test_encrypt**():

		No documentation available


- **test_message_key**():

		No documentation available


- **test_password_key**():

		No documentation available
