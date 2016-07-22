pride.persistence
==============



load_data
--------------

**load_data**(packed_data):

				No documentation available


pack_data
--------------

**pack_data**(arg):

		 Pack arguments into a stream, prefixed by size headers.
        Resulting bytestream takes the form:
            
            size1 size2 size3 ... sizeN data1data2data3...dataN
            
        The returned bytestream can be unpacked via unpack_data to
        return the original contents, in order. 


save_data
--------------

**save_data**(args):

				No documentation available


unpack_data
--------------

**unpack_data**(packed_data):

				No documentation available
