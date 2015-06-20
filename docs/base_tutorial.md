Crash course
============

There is a root inheritance object named mpre.base.Base. Classes that inherit from Base
will inherit a number of convenient methods and features. 
                    
Base objects utilize a class.defaults dictionary. This dictionary contains
attribute:value pairs that will automatically be assigned to new instances
upon call to Base.\_\_init\_\_. Base objects specify arguments when initializing
via keyword arguments. Attributes specified this way will override
class default attributes.

    
    class Test_Class(mpre.base.Base):
        defaults = mpre.base.Base.defaults.copy()
        defaults.update({"test_attribute" : 'value',
                         "test_attribute2" : 100})
                         
    test_class = Test_Class(new_attribute="Testing", test_attribute=0.0)
    print test_class.new_attribute
    print test_class.test_attribute
    print test_class.test_attribute2
    

class.defaults also provide the information required for automatic command line
argument parsing. By setting parse_args=True to, attributes of the instance
can be assigned at program launch via command line arguments. Note this only
works for attributes in the defaults dictionary.


    class Test_Class(mpre.base.Base):
        
        defaults = mpre.base.Base.defaults.copy()
        defaults.update({"test_flag" : True})
        
    test_class = Test_Class(parse_args=True)
    
    
In the above example, the attribute "test_flag" on the instance test_class could
potentially be set by supplying --test_flag False on the command line when launching
the program.


Concurrency
===================
Concurrency is facilitated by being single threaded. All operations may proceed as 
if they were atomic and no locking primitives are required. Each component generally only acts
on data in its self namespace, the instance __dict__ attribute. Certain actions, such as 
creating new instances, have effects on the mpre.environment object. This object stores
global data including the components dictionary used to lookup instance names.

There are two mechanisms for local concurrency. The immediate method involves looking up
the component name of the desired instance and getting the associated instance from
mpre.components. Here is an example:
    
    
    def send_data(self, data):
        # lookup the instance known as self.target_component and call instance.handle_data(data)
        result = mpre.components[self.target_component].handle_data(data)
        
        
The futures method involves the use of mpre.Instruction objects. Instructions 
are created with a component name, method name, and any positional/keyword 
arguments for the method. These objects have an execute method which schedules
the instruction to be performed in the specified number of seconds. These 
instructions are not performed in the current scope and require the attachment
of a callback if access to the return value is required:
            
    
    class Test_Component(mpre.base.Base):
        def __init__(self, **kwargs):
            self.update_instruction = Instruction(self.instance_name, 
                                                  "update").execute(priority=60,
                                                                    callback=self.schedule_update)
                                                                    
        def update(self):
            new_instance = super(Test_Component, self).update()
            new_instance.update_instruction.execute(priority=60,
                                                    callback=new_instance.schedule_update)
            

The above component, once initialized, will update itself from the source code
on disk every 60 seconds. This also demonstrates the update method. Due to the
fact that components are referenced by string, updating them is in general
a matter of rearranging the environment references of the old component with a
newly created one. The update method preserves attributes across updated 
instances.

Distributed concurrency is also handled by the Instruction object. This works
in the same way that the previous futures concurrency demonstration did, except
a host_name is specified to the Instruction.execute call. This host_name attribute
is a (ip_address, port) 2-tuple. Provided there is a reachable host at this 
address with a metapython process running and the named component present, the
instruction will be performed transparently on the remote host. Note that 
authentication via ssl and the secure remote password protocol are in the works
to secure access between hosts, but are not yet available in a suitable form.

    def load_file(_file):
        file_object = mpre.base.load(_file)
        print file_object.read()
        
    Instruction("File1", "save").execute(host_info("192.168.1.222", 40022),
                                         callback=load_file)
                                         
                                         
The above also demonstrates use of the save and load methods. Base objects
can be preserved indefinitely via the save method. The bytestream produced
by this method can be supplied to mpre.base.Base.load (or mpre.base.load, they
are the same) and the component will be restored. The save and load methods
are slightly higher level then basic pickling and will not balk at updated
components. The attributes and the information required to reconstruct an
equivalent object are preserved. In addition, bytestreams have a message
authentication code attached which prevents tampering. Note that this feature
is not fully secure in its current implementation.


Process objects
===================
Certain needs require events that occur at explicitly set intervals. This need
is met by mpre.vmlibrary.Process objects. These objects fit a similar interface
to pythons threading.Thread and multiprocessing.Process objects. Namely, they 
have a start and run method. Process objects have a running attribute. While
this attribute equals True, after running an instruction for process_instance.run 
will be executed for process_instance.priority seconds. For closing, Process 
objects are deleted instead of joined. 


Network sockets
===================
Networking is facilitated via mpre.network. This module contains Wrappers 
around pythons socket.socket objects. These wrappers have their recv
calls event triggered by select.select. Sockets are customized for
the application in question via extending the recv/recvfrom method.

Note that Instruction objects can execute calls on remote machines by 
specifying host information. This probably the most straightforward way to
communicate application logic between machines, in terms of readability 
and development time. 

Pickling and unpickling do take time though, so it is potentially more
performant to extend sockets and write specific logic for the application in
question. This is probably more true with applications that exchange very
simple data very frequently. Applications that hope to share python objects
will probably not benefit greatly from extending sockets as opposed to using
Instructions.


Pre existing projects
===================
If you have your own application developed and your own inheritance structure
set, you can still make use of the features provided by a Base object. The
mpre.base module provides Wrapper and Proxy classes that act simultaneously
as the wrapped object and as a Base object. These objects automatically
acquire the attributes of the object they wrap, in different priority. The
attributes of a Wrapper object will only be accessed if the attribute was
not available on the wrapped object. The attributes of a Proxy object will
be gotten/set before using the wrapped objects attributes.

A reference for non Base objects can be acquired by instantiating the
object in question via the create factory method instead of instantiating
the object directly. The objects instance name will be determined in the 
same manner as a Base objects, that is it's __class__.__name__ + the
number of such instances created so far.