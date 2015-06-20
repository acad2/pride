mpre
==============



Alert_Handler
--------------

	 Provides the backend for the base.alert method. This component is automatically
        created by the Metapython component. The print_level and log_level attributes act
        as global filters for alerts; print_level and log_level may be specified as 
        command line arguments upon program startup to globally control verbosity/logging.


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'log_is_persistent': False,
	 'log_level': 0,
	 'log_name': 'Alerts.log',
	 'parse_args': True,
	 'print_level': 0,
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'mpre.Alert_Handler'>, <class 'mpre.base.Base'>, <type 'object'>)

Environment
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.Environment'>, <type 'object'>)

- **modify**(self, container_name, item, method):

				No documentation available


- **update**(self, environment):

				No documentation available


- **replace**(self, component, new_component):

				No documentation available


- **add**(self, instance):

				No documentation available


- **preserved**(, *args, **kwds):

				No documentation available


- **display**(self):

				No documentation available


- **delete**(self, instance):

				No documentation available


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
            
            host_info may be specified to designate a remote machine that
            the Instruction should be executed on. If host_info is supplied
            and callback is None, the results of the instruction will be 
            supplied to RPC_Handler.alert.
