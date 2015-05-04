mpre.vmlibrary
==============



Instruction
--------------

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
        that they do not happen inline even if the priority is 0.0. In
        order to access the result of the executed function, a callback
        function can be provided.


Method resolution order: 

	(<class 'mpre.Instruction'>, <type 'object'>)

- **execute**(self, priority, callback, host_info, transport_protocol):

		 usage: instruction.execute(priority=0.0, callback=None)
        
            Submits an instruction to the processing queue. The instruction
            will be executed in priority seconds. An optional callback function 
            can be provided if the return value of the instruction is needed.


Process
--------------

	 usage: Process(target=function, args=..., kwargs=...) => process_object
    
        Create a logical process. Note that while Process objects
        allow for the interface of target=function, the preferred usage
        is via subclassing.
        
        Process objects have a run_instruction attribute. This attribute
        is a saved instruction: Instruction(self.instance_name, 'run'). 
        
        Process objects have a default attribute 'auto_start', which
        defaults to True. When True, an instruction for process.start
        will automatically be executed inside __init__.
        
        The start method simply calls the run method, but can be overriden 
        if the entry point would be useful, and keeps a similar interface
        with the standard library threading/process model.
        
        Subclasses should overload the run method. A process may propagate
        itself by executing a run instruction inside it's run method. While
        processes support the reaction interface, use of a process presumes
        the desire for some kind of explicitly timed Instruction. Examples
        of processes include polling for user input or socket buffers
        at various intervals.
        
        Some people may find the serial style, one frame at a time method
        offered by processes easier to understand and follow then reactions.
        Most things can be accomplished by either, though processes may be
        less performant then parallel_methods/reactions


Instance defaults: 

	{'_deleted': False,
	 'auto_start': True,
	 'priority': 0.04,
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.vmlibrary.Process'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **run**(self):

		No documentation available


- **start**(self):

		No documentation available


Processor
--------------

	 Removes enqueued Instructions via heapq.heappop, then
        performs the specified method call while handling the
        possibility of the specified component/method not existing,
        and any exception that could be raised inside the method call
        itself.


Instance defaults: 

	{'_deleted': False,
	 'auto_start': False,
	 'priority': 0.04,
	 'replace_reference_on_load': True,
	 'running': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.vmlibrary.Processor'>,
	 <class 'mpre.vmlibrary.Process'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **pause**(self, component_name):

		No documentation available


- **run**(self):

		No documentation available


- **resume**(self, component_name):

		No documentation available


partial
--------------

	partial(func, *args, **keywords) - new function with partial application
    of the given arguments and keywords.



Method resolution order: 

	(<type 'functools.partial'>, <type 'object'>)