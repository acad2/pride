pride.utilities
==============



convert
--------------

**convert**(old_value, old_base, new_base):

		 Converts a number in an arbitrary base to the equivalent number
        in another. 
        
        old_value is a string representation of the number to be converted,
        represented in old_base.
        
        new_base is the symbol set to be converted to.
        
        old_base and new_base are iterables, most commonly string or list. 


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


isancestor
--------------

**isancestor**(ancestor, descendant):

		 usage: isancestor(ancestor, descendant) => (True or False)
    
        Returns True if ancestor is an ancestor of descendant (i.e. a parent, grandparent, great grandparent, etc).
        Returns False is ancestor is not an ancestor of descendant.
        
        Note that this method only works with Base objects. 


isdescendant
--------------

**isdescendant**(descendant, ancestor):

		 usage: isdescendant(descendant, ancestor)
        
        Returns True if ancestor is an ancestor of descendant (i.e. a parent, grandparent, great grandparent, etc).
        Returns False is ancestor is not an ancestor of descendant.
        
        Note that this method only works with Base objects. 


load_data
--------------

**load_data**(packed_data):

				No documentation available


print_in_place
--------------

**print_in_place**(_string):

				No documentation available


rotate
--------------

**rotate**(input_string, amount):

		 Rotate input_string by amount. Amount may be positive or negative.
        Example:
            
            >>> data = "0001"
            >>> rotated = rotate(data, -1) # shift left one
            >>> print rotated
            >>> 0010
            >>> print rotate(rotated, 1) # shift right one, back to original
            >>> 0001 


save_data
--------------

**save_data**(args):

				No documentation available


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


splice
--------------

**splice**(new_bytes, into, at):

				No documentation available


test_isancestor_isdescendant
--------------

**test_isancestor_isdescendant**():

				No documentation available


test_pack_unpack
--------------

**test_pack_unpack**():

				No documentation available


updated_class
--------------

**updated_class**(_class):

				No documentation available


usage
--------------

**usage**(_object):

				No documentation available
