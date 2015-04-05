mpre.vmlibrary
========
No documentation available

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

Process
--------
	 usage: Process(target=function, args=..., kwargs=...) => process_object
	
	Create a serial logical process. Note that while Process objects
	allow for the interface of target=function, the preferred usage
	is via subclassing.
	
	Process objects have a run_instruction attribute. This attribute
	is a saved instruction: Instruction(self.instance_name, 'run'). 
	
	Process objects have a default attribute 'auto_start', which
	defaults to True. When True, an instruction for process.start
	will automatically be executed inside __init__.
	
	The start method simply calls the run method, but can be overriden 
	if the entry point would be useful, and keeps a similar interface
	with the threading/process model.
	
	Subclasses should overload the run method. A process may propagate
	itself by executing a run instruction inside it's run method. While
	processes support the reaction interface, use of a process presumes
	the desire for some kind of explicitly timed Instruction. Examples
	of processes include polling for user input or socket buffers
	at various intervals.
	
	Some people may find the serial style, one frame at a time method
	offered by processes easier to understand and follow then reactions.
	Most things can be accomplished by either.

Default values for newly created instances:

- priority                 0.04
- memory_size              4096
- auto_start               True
- memory_mode              -1
- update_flag              False
- deleted                  False
- verbosity                

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **start**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Processor
--------
	 Removes enqueued Instructions via heapq.heappop, then
	performs the specified method call while handling the
	possibility of the specified component/method not existing,
	and any exception that could be raised inside the method call
	itself.
	
	Essentially a task manager for launching other processes.

Default values for newly created instances:

- priority                 0.04
- running                  True
- memory_size              4096
- memory_mode              -1
- auto_start               False
- update_flag              False
- deleted                  False
- verbosity                

This object defines the following non-private methods:


- **run**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.vmlibrary.Processor', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


partial
--------
partial(func, *args, **keywords) - new function with partial application
    of the given arguments and keywords.
