mpre.utilities
==============



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

	(<class 'mpre.utilities.Average'>, <type 'object'>)

- **full_add**(self, value):

				No documentation available


- **partial_add**(self, value):

				No documentation available


LRU_Cache
--------------

	A dictionary with a max size that keeps track of
       key usage and handles key eviction. 
       
       currently completely untested


Method resolution order: 

	(<class 'mpre.utilities.LRU_Cache'>, <type 'object'>)

Latency
--------------

	 usage: Latency([name="component_name"], 
                       [size=20]) => latency_object
                       
        Latency objects possess a latency attribute that marks
        the average time between calls to latency.update()


Method resolution order: 

	(<class 'mpre.utilities.Latency'>, <type 'object'>)

- **finish_measuring**(self):

				No documentation available


- **start_measuring**(self):

				No documentation available


Reversible_Mapping
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.utilities.Reversible_Mapping'>, <type 'object'>)

- **reverse_lookup**(self, value):

				No documentation available


convert
--------------

**convert**(old_value, old_base, new_base):

				No documentation available


documentation
--------------

**documentation**(_object):

				No documentation available


function_header
--------------

**function_header**(function):

		usage: function_header(function) => "(arg1, default_arg=True, keyword=True...)"
    
       Given a function, return a string of it's signature.


function_names
--------------

**function_names**(function):

				No documentation available


resolve_string
--------------

**resolve_string**(string):

		Given an attribute string of a.b...z, return the object z


shell
--------------

**shell**(command, shell):

		 usage: shell('command string --with args', 
                     [shell=False]) = > sys.stdout.output from executed command
                    
        Launches a process on the physical machine via the operating 
        system shell. The shell and available commands are OS dependent.
        
        Regarding the shell argument; from the python docs on subprocess.Popen:
            "The shell argument (which defaults to False) specifies whether to use the shell as the program to execute. If shell is True, it is recommended to pass args as a string rather than as a sequence."
            
        and also:        
            "Executing shell commands that incorporate unsanitized input from an untrusted source makes a program vulnerable to shell injection, a serious security flaw which can result in arbitrary command execution. For this reason, the use of shell=True is strongly discouraged in cases where the command string is constructed from external input" 


sys_argv_swapped
--------------

**sys_argv_swapped**(, *args, **kwds):

				No documentation available


updated_class
--------------

**updated_class**(_class, importer_type):

				No documentation available


usage
--------------

**usage**(_object):

				No documentation available
