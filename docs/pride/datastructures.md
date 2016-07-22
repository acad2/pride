pride.datastructures
==============

 Module for datastructures of various kinds. Objects defined here may not 
    be employed elsewhere in pride; they're just potentially generally useful 
    and not already defined in the standard library (to my knowledge) 
    
    Objects defined here should not rely on pride for anything - regular python only. 

Average
--------------

	 usage: Average([name=''], [size=20], 
                       [values=tuple()], [meta_average=False]) => average_object
                       
        Average objects keep a running average via the add method.
        The size option specifies the maximum number of samples. When
        this limit is reached, additional samples will result in the
        oldest sample being removed.
        
        values may be used to seed the average.
        
        The meta_average boolean flag is used to determine whether or not
        to keep an average of the average - This is implemented by an
        additional Average object.


Method resolution order: 

	(<class 'pride.datastructures.Average'>, <type 'object'>)

- **full_add**(self, value):

				No documentation available


- **partial_add**(self, value):

				No documentation available


Index_Preserving_List
--------------

	 A list that preserves the index of each item when an item is added or removed. 


Method resolution order: 

	(<class 'pride.datastructures.Index_Preserving_List'>, <type 'object'>)

- **remove**(self, item):

				No documentation available


- **unit_test**():

				No documentation available


- **append**(self, item):

				No documentation available


LRU_Cache
--------------

	A dictionary with a max size that keeps track of
       key usage and handles key eviction. 
       
       currently completely untested


Method resolution order: 

	(<class 'pride.datastructures.LRU_Cache'>, <type 'object'>)

Latency
--------------

	 usage: Latency([name="component_name"], 
                       [size=20]) => latency_object
                       
        Latency objects possess a start_measuring and )


Method resolution order: 

	(<class 'pride.datastructures.Latency'>, <type 'object'>)

- **mark**(self):

				No documentation available


Reversible_Mapping
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.datastructures.Reversible_Mapping'>, <type 'object'>)

- **items**(self):

				No documentation available


- **reverse_lookup**(self, value):

				No documentation available
