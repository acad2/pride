Making things easy
================
Setting attributes programmatically
----------------
A standard CPython class definition might look like the following:

    # base_tutorial_code.py
    class Base(object):
        """A root inheritance object that establishes framework-wide features"""
        
        def __init__(self, memory_size=8192, network_packet_size=4096):
            self.memory_size = memory_size
            self.network_packet_size = network_packet_size
    
    
    >>> base_object = Base()
    >>> base_object.memory_size
    >>> 8192
    >>> base_object.network_chunk__size
    >>> 4096
    
Repetition and patterns indicate something that could be in a function. Note
that both memory_size and network_size were used three times in this call, and that 
two of the same operation (x = y) were performed consecutively. This factor influences 
the line count of the source code and here the number scales with the number of 
arguments to \_\_init\_\_.
            
Base objects set their attributes programmatically, so the number of lines required to 
set attributes inside \_\_init\_\_ is constant. Here's an equivalent example to above
with programmatically defined attributes.

    class Base(object):
        
        def __init__(self, **kwargs):
            self.set_attributes(**kwargs)
            
        def set_attributes(self, **kwargs):
            """
            base_object.set_attributes(attribute=value, attribute2=value2, ...)
            
            The supplied keyword arguments are interpreted as attribute-value pairs
            and set as attributes on the calling object
            """
            [setattr(self, attribute, value) for attribute, value in kwargs.items()]

    >>> base_object = Base(memory_size=8192, network_packet_size=4096)
    >>> base_object.memory_size
    >>> 8192
    >>> base_object.network_packet_size
    >>> 4096

A base object can have any attributes assigned at instance creation by specifying them as 
keyword arguments. This simple feature helps to simplify code management by a good amount for
large projects.
            
Defaults
----------------
Classes that inherit from base should specify a class.defaults dictionary. A new subclass
can "inherit" it's ancestors defaults by making a copy of the dictionary. 

This dictionary contains attribute:value pairs that will automatically be assigned to new instances. When an instance is initialized, this dictionary is copied and the copy updated with any kwargs
supplied to the constructor. This temporary dictionary is then provided to the set_attribute method
outlined in the previous section. 

This means that default attributes/values will be present on new instances unless those
attributes were specified otherwise via kwargs. An example:
    
    class DefaultsDemo(mpre.base.Base):
        
        # "inherit" Base defaults
        defaults = mpre.defaults.Base.copy()
        
        # specialize/update the defaults
        defaults.update({"filepath" : '',
                         "count" : 0,
                         "message" : "default"})
        ...   
            
    >>> demo = DefaultsDemo()
    >>> demo.filepath
    >>> ''
    >>> demo.count
    >>> 0
    >>> demo.message
    >>> "default"
    
    >>> demo2 = DefaultsDemo(filepath="~/", not_listed=True)
    >>> demo2.filepath
    >>> "~/"
    >>> demo2.count
    >>> 0
    >>> demo2.not_listed
    >>> True
    
Instance names and numbers
------------------

Base objects each have their own unique string identifier. This identifier
consists of the name of the type of the instance concatenated with the instance
number. The instance number is equal to the number of instances of that class
that have been instantiated so far. The identifier or instance_name of the fifth
instance of class Demo_Class would be "Demo_Class4". Note the
use of zero based indexing, and also that the zero instance is referred to
simply as "Demo_Class" with the 0 omitted. The actual code for this is in
mpre.base.Base\_\_init\_\_ and is copied here for example:

    ...
    def __init__(self, **kwargs):
        super(Base, self).__init__()
        
        # register name + number
        cls = type(self)
        
        instance_number = self.instance_number = cls.instance_count
        cls.instance_tracker[instance_number] = self
        cls.instance_count += 1
        
        ending = str(instance_number) if instance_number else ''
        name = self.instance_name = cls.__name__ + ending
        Component_Resolve[name] = self        
        ...
 
These names can be used to reference the actual object from anywhere via 
Instructions, the send_to method, and public methods.

Instructions
-------------

Instruction objects are a way to call a method on a foreign process without
needing the process to be in the current scope. Instructions, when instantiated,
are given a component name (as above), the name of a method that the object possesses 
that will be called, and any arguments/keyword arguments needed by that call.
Here's a trivial example:
    
    # without instructions, the object must be within scope or
    # accessed via doc notation externally
    processa = ProcessA()
    
    class ProcessB(mpre.vmlibrary.Process):
        ...
        def run(self):
            processa.do_something(1, "demo_argument", keyword=True)
            # or
            external_module.processa.do_something(1, "demo_argument", keyword=True)
            
            
    # with instructions:
    
    class ProcessB(mpre.vmlibrary.Process):
        ...
        def run(self):
            # the component ProcessA could be local or foreign, as long
            # as it has been created it does not matter where it is.
            Instruction("ProcessA", "do_something", 
                         1, "demo_argument", 
                         keyword=True).execute()
                         
            # second example: perpetuate this method
            run_instruction = Instruction(self.instance_name, "run")
            run_instruction.priority = self.priority
            run_instruction.execute()            
            
            # that run_instruction is so common it exists automatically
            # so don't do the above, instead do this:
            self.run_instruction.execute()
            
Instructions may be used to reference any Base object including local ones. 
This is useful because the component.method call that the Instruction was supplied with 
does not happen immediately. It is scheduled according to its priority attribute. This
attribute defaults to 0.0. This value is in seconds, and a value of 0.0 is the
highest priority and would be scheduled immediately. 

Instruction objects have an execute method. This method places the 
instruction into the processing queue scheduled at the current time + instruction.priority. 
This also allows Instruction objects to be reusable.

mpre.vmlibrary.Process objects have a default priority attribute. The default value is .04 
and may be modified by changing your_process_subclass.defaults or via keyword argument when 
instantiating a process.  Process objects also have a run_instruction attribute. 
This attribute is created as we did in the second example above, except that the instruction 
is saved as self.run_instruction instead of executed. 

Public Methods
--------------

Sometimes it is desirable to allow direct, immediate, foreign access to a method. For
example, when one adds a socket to an mpre.networklibrary.Asynchronous_Network, it calls
only a few lines of code, and is usually scheduled to happen immediately. Instructions
are overkill in such a situation, and this is where public methods come in. 

A class may specify a public_methods attribute, which is a container of method names in the
form of strings. This marks these methods as accessible to the method base.public_method. 
A method that is not in this container cannot be called via a public_method call.
This methods argument signature is identical to Instruction objects. Unlike instructions,
a public_method call happens immediately in the current scope, and any return value is accessible
for use in the current scope. Here's an example:

    # a class that defines public_methods
    class Test(mpre.base.Base):
        public_methods = ("add_to_buffer", "mutate")
        ...
        def add_to_buffer(self, instance):
            self.buffer.append(instance)
            
        def mutate(self, data):
            return data ** 2 * 2 / 2
            
    test = Test()
    
    # via Instruction objects:
    class TestProcess(mpre.vmlibrary.Process):
        ...
        def run(self):
            Instruction("Test", "add_to_buffer", self).execute()
            
            # note that because this instruction is scheduled and does not
            # happen immediately, there is no (practical) way to access
            # the return value, so this instruction can't accomplish anything
            # unless self.data is a mutable datatype (no strings or numbers)
            Instruction("Test", "mutate", self.data).execute()
            
            
    # with public methods instead:
    class TestProcess(mpre.vmlibrary.Process):
        ...
        def run(self):
            
            # no context change required for the single line of code this method uses
            self.public_method("Test", "add_to_buffer", self)
            
            # The return value is accessible and Test.mutate plays well
            # with any data type, including strings and numbers.
            mutated_data = self.public_method("Test", "mutate", self.data)
            
send_to and read_messages
-------------------------
The third situation where instance names can be used is in the send_to and 
read_messages methods. send_to accepts a component name and a bytes/string
argument. These bytes are written to a chunk of memory owned by the specified
component_name. read_messages returns an iterable containing any messages
that were sent between now and the last call to read_messages. Here's an example:

    class Audio_Broadcaster(mpre.vmlibrary.Process):
        ...
        def run(self):
            # read_messages returns packets of audio data sent from an Audio_Generator. 
            # Note that read messages returns an iterable of message 'packets'
            # as opposed to the raw bytes that were contained in memory
            # so it is safe to receive packets at asynchronous intervals
            for audio_data in self.read_messages():
                self.send_to_clients(audio_data)
            ...
            
    class Audio_Generator(mpre.vmlibrary.Process):
        def run(self):
            if self.audio_data:
                # send a single message "packet" of self.audio_data to Audio_Broadcaster
                self.send_to("Audio_Broadcaster", self.audio_data)
            ...
        
Note that messages are written/read in "packets". read_messages does not return
the bytes string contained in memory, but an iterable which contains each separate 
bytes/string that was sent. This enables the receiver to receive possibly multiple 
packets from a number of sources and have them remain separate without needed
code for delimiters/fixed length messages/etc.
        
It is possible to achieve the same effect as above with instructions/public methods.
Which you use is at this point mostly a matter of personal preference.
        
      
Creation/Deletion and .objects       
--------------

Base objects have create and delete methods. The create method is a dispatcher for
object instantiation. It accepts an instance_type argument, which is either a class/type
or a "module_name.Class_Name" string. It also accepts any positional/keyword arguments
that instance_type can use. If a string is passed as the instance_type, the specified
package/module will be imported and the class accessed as an attribute of that module.
The create method returns the instantiated object. 

It also calls the add method on the new instance, which adds the instance to parent_object.objects.
This is another attribute that Base objects come preloaded with. The .objects attribute
is a dictionary whose keys are type names and whose values are lists containing
instances of that type. This dictionary tracks instances that have been created.

The add method also tracks where the instance is stored, so that the remove method
can later remove the instance from those places when the object is being deleted. The
delete argument is fairly self explanatory. It takes no arguments and removes all
the known references to it. The object will be no longer be valid as a reference
to Instructions/public_methods/messaging and will be garbage collected. 

The add and remove methods are somewhat of a backend feature. While they are not
explicitly private methods, there should be little need to override them. In such
situations, ensure super is called so that references can be cleared.

Note that this feature is not foolproof, it is possible to add an instance to a container
that is not tracked via the add method. In such situations, be sure to extend
the delete method to explicitly attempt removal of the object from any containers
so that the object can be deleted reliably.

Alerts
-----------------
Base objects feature an alert method. This method takes a string message, and optionally any
of:
    
    - an iterable containing string format args for the message
    - a level keyword argument. default is 0, successive levels of 'v' are used
    - a callback function
    - a callback Instruction
    
The alert method checks the level value against the objects verbosity attribute.
The possible values are 0, 'v', 'vv', 'vvv', ... 0 indicates an error, and successively
sized 'v' levels indicate successively more verbose messages. 

If the message level is within the range of the objects verbosity, then the iterable of string format
args is formatted into the message (if any). This is done here to save a few operations when
verbose messages aren't going to be printed anyways. If preferred, one could supply
a pre-formatted string as the message and not supply format args. This may result in
wasted operations for the above reason.

Afterwards, the level is checked against mpre.base.Alert's print_level and log_level settings.
If they are within range, the message is printed and/or logged accordingly. 

These values can be adjusted as needed by the user. They both default to 0.

    - setting log_level to 'v' means alerts that are 'vv' or higher level will not be logged to disk.
      the default behavior of 0 logs only errors.
      
    - print_level is a global filter option. when 0, it does not filter any messages. 
      when set, messages that are at a lower level then print_level will be printed. 
      If print_level were set to 'vvv', messages that were 0-'vvv' would print, while
      'vvvv' or more would not print regardless of level or object verbosity.
      
Alerts also accept callback instructions and callback functions. These are only 
executed if the message level is within the objects verbosity. The print_level and log_level
settings do not interfere with callbacks. A demonstration:
    
    class CallbackDemo(mpre.base.Base):
        ...
        def doing_work(self):
            try:
                this_might_not_work()
            except IOError as exception:
                self.alert("IOError in {}.doing_work\n{}", 
                           format_args=[self.instance_name, exception.message],
                           callback_instruction=Instruction(self.instance_name, "pause_work"),
                           callback=(self.pre_pause, [exception], {}))
        ...

        
Note that the callback is a 3-tuple of (method, args, kwargs)

More detail
-------------
A more in depth view can be found at the documentation for the mpre.base module, or by reading
the source code/docstrings (which the documentation is derived from!)