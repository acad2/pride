mpre.misc.attributetest
========
No documentation available

Persistent_Reactor
--------
	No docstring found

Default values for newly created instances:

- deleted                  False
- verbosity                
- memory_size              4096
- memory_mode              -1
- update_flag              False

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.misc.attributetest.Persistent_Reactor', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Struct
--------
No documentation available

izip
--------
izip(iter1 [,iter2 [...]]) --> izip object

Return a izip object whose .next() method returns a tuple where
the i-th element comes from the i-th iterable argument.  The .next()
method continues until the shortest iterable in the argument sequence
is exhausted and then it raises StopIteration.  Works like the zip()
function but consumes less memory by returning an iterator instead of
a list.