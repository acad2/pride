pride.vmlibrary
==============



Idle_Process
--------------

	No docstring found


Instance defaults: 

	{'_run_queued': False,
	 'context_managed': False,
	 'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'priority': 300.0,
	 'replace_reference_on_load': True,
	 'reschedule_run_after_exception': True,
	 'run_callback': None,
	 'run_condition': '',
	 'running': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.vmlibrary.Idle_Process'>,
	 <class 'pride.vmlibrary.Process'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **run**(self):

				No documentation available


- **register_callback**(self, reference, method_name, single_use):

				No documentation available


Instruction
--------------

	 usage: Instruction(component_name, method_name,
                           *args, **kwargs).execute(priority=priority,
                                                    callback=callback)

            - component_name is the string reference of the component
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.


        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will be performed. Instructions are useful for explicitly
        timed/recurring tasks.

        Instructions may be reused. The same instruction object can be
        executed any number of times.

        Note that Instructions must be executed to have any effect, and
        that they do not happen inline even if the priority is 0.0. In
        order to access the result of the executed function, a callback
        function can be provided.


Method resolution order: 

	(<class 'pride.Instruction'>, <type 'object'>)

- **execute**(self, priority, callback):

		 usage: instruction.execute(priority=0.0, callback=None)

            Submits an instruction to the processing queue.
            The instruction will be executed in priority seconds.
            An optional callback function can be provided if the return value
            of the instruction is needed. 


- **purge**(cls, reference):

				No documentation available


- **unschedule**(self):

				No documentation available


Process
--------------

	 usage: Process(target=function, args=..., kwargs=...) => process_object
    
        Create a virtual process. Note that while Process objects
        allow for the interface of target=function, the preferred usage
        is via subclassing.       
        
        The start method simply calls the run method, but can be overriden 
        if the entry point would be useful, and keeps a similar interface
        with the standard library threading/process model.
        
        Subclasses should overload the run method. Use of a process 
        object presumes the desire for some kind of explicitly timed
        or periodic event.


Instance defaults: 

	{'_run_queued': False,
	 'context_managed': False,
	 'deleted': False,
	 'dont_save': False,
	 'parse_args': False,
	 'priority': 0.04,
	 'replace_reference_on_load': True,
	 'reschedule_run_after_exception': True,
	 'run_callback': None,
	 'run_condition': '',
	 'running': True,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.vmlibrary.Process'>, <class 'pride.base.Base'>, <type 'object'>)

- **run**(self):

				No documentation available


- **on_load**(self, state):

				No documentation available


- **handle_instruction_exception**(self, method, error, callback, result):

				No documentation available


- **start**(self):

				No documentation available


- **delete**(self):

				No documentation available


Processor
--------------

	 Removes enqueued Instructions via heapq.heappop, then
        performs the specified method call while handling the
        possibility of the specified component/method not existing,
        and any exception that could be raised inside the method call
        itself.


Instance defaults: 

	{'_run_queued': False,
	 'context_managed': False,
	 'deleted': False,
	 'dont_save': False,
	 'execution_verbosity': 'vvvv',
	 'parse_args': True,
	 'priority': 0.04,
	 'replace_reference_on_load': True,
	 'reschedule_run_after_exception': True,
	 'run_callback': None,
	 'run_condition': '',
	 'running': False,
	 'startup_components': ()}

Method resolution order: 

	(<class 'pride.vmlibrary.Processor'>,
	 <class 'pride.vmlibrary.Process'>,
	 <class 'pride.base.Base'>,
	 <type 'object'>)

- **run**(self):

				No documentation available


partial
--------------

	partial(func, *args, **keywords) - new function with partial application
    of the given arguments and keywords.



Method resolution order: 

	(<type 'functools.partial'>, <type 'object'>)