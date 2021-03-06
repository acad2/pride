network2
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


- **execute(self, priority, callback, host_info, transport_protocol):

		 usage: instruction.execute(priority=0.0, callback=None)
        
            Submits an instruction to the processing queue. The instruction
            will be executed in priority seconds. An optional callback function 
            can be provided if the return value of the instruction is needed.


- **test_authentication():

		No documentation available


- **test_file_service():

		No documentation available


- **test_proxy():

		No documentation available


- **test_reliability():

		No documentation available


- **test_rpc():

		No documentation available
