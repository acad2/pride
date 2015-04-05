mpre.demo_a
========
No documentation available

Concurrency_Demo
--------
	No docstring found

Default values for newly created instances:

- priority                 1
- memory_size              4096
- memory_mode              -1
- update_flag              False
- deleted                  False
- verbosity                
- counter                  0

This object defines the following non-private methods:


- **synchronized_message**(self):

		  No documentation available



- **test_method**(self, input):

		  No documentation available


This objects method resolution order is:

(class 'mpre.demo_a.Concurrency_Demo', class 'mpre.base.Base', type 'object')


Instruction
--------
 usage: Instruction(component_name, method_name, 
                           *args, **kwargs).execute(priority=priority)
                           
        Creates and executes an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds. 
        
        Instructions may be saved as an attribute of a component instead
        of continuously being instantiated. This allows the reuse of
        instruction objects. The same instruction object can be executed 
        any number of times.
        
        Note that Instructions must be executed to have any effect, and
        that they do not happen inline, even if priority is 0.0. 
        Because they do not execute in the current scope, the return value 
        from the method call is not available through this mechanism.