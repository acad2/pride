mpre.vmlibrary
========
No documentation available

Instruction
--------
No documentation available

Machine
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- memory_size              4096
- deleted                  False
- verbosity                
- system_configuration     (('vmlibrary.System', (), {}),)
- processor_count          1

This object defines the following non-private methods:


- **run**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.vmlibrary.Machine', class 'mpre.base.Base', type 'object')


Process
--------
	a base process for processes to subclass from. Processes are managed
	by the system. The start method begins a process while the run method contains
	the actual code to be executed every frame.

Default values for newly created instances:

- network_packet_size      4096
- keyboard_input           
- deleted                  False
- verbosity                
- priority                 0.04
- memory_size              4096
- network_buffer           
- auto_start               True

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **process**(self, method_name, *args, **kwargs):

		  No documentation available



- **start**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.vmlibrary.Process', class 'mpre.base.Base', type 'object')


Processor
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- deleted                  False
- verbosity                
- memory_size              4096
- _cache_flush_interval    15

This object defines the following non-private methods:


- **run**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.vmlibrary.Processor', class 'mpre.base.Base', type 'object')


System
--------
	a class for managing components and applications.
	
	usually holds components such as the instruction handler, network manager, display,
	and so on. hotkeys set at the system level will be called if the key(s) are
	pressed and no other active object have the keypress defined.

Default values for newly created instances:

- network_packet_size      4096
- status                   
- name                     system
- deleted                  False
- verbosity                
- memory_size              4096
- startup_processes        ()
- hardware_configuration   ()

This object defines the following non-private methods:


- **run**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.vmlibrary.System', class 'mpre.base.Base', type 'object')


Thread
--------
	does not run in parallel like threading.thread

Default values for newly created instances:

- network_packet_size      4096
- deleted                  False
- verbosity                
- memory_size              4096

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **start**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.vmlibrary.Thread', class 'mpre.base.Base', type 'object')


attrgetter
--------
attrgetter(attr, ...) --> attrgetter object

Return a callable object that fetches the given attribute(s) from its operand.
After f = attrgetter('name'), the call f(r) returns r.name.
After g = attrgetter('name', 'date'), the call g(r) returns (r.name, r.date).
After h = attrgetter('name.first', 'name.last'), the call h(r) returns
(r.name.first, r.name.last).

deque
--------
deque([iterable[, maxlen]]) --> deque object

Build an ordered collection with optimized access from its endpoints.

partial
--------
partial(func, *args, **keywords) - new function with partial application
    of the given arguments and keywords.
