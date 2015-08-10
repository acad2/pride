Certificate configuration and Registration
---------------
This is a required step to have access to the command line shell.


Configuring ssl
---------------

ssl servers require certificates. You can generate a self signed certificate
for a server by running the command:
    
    python ./programs/create_self_signed_certificate.py
    
This will generate the required server.crt, server.csr, and server.key files. Note that you can generate files by other names through the --name keyword.
The names of the .key, .csr, and .crt files should be supplied in the
defaults in the appropriate SSL_Server class definition.

Account creation
---------------

Remote access to the environment requires authentication. In the mpre.programs
package there is a file called register.py. It can be used to register
an account with a desired service. The authentication client for the
service is specified via the --client_name keyword. For example:

    python metapython.py ./programs/register.py --client_name mpre.rpc.Environment_Access_Client
    
    python metapython.py ./programs/register.py --client_name mpre._metapython.Shell
        
The above attempts to register an account with the Environment_Access service,
which is the component that oversees remote access to the machine. A user
logged in to this service can make remote procedure calls to any object
in the environment that has an instance_name reference. Note that
certain components may also require an additional level of authentication. 
The second command attempts to register for access to the command line shell.

In the above example, no --ip flag is supplied. This results in the commands
attempting to register on the local machine.  

You can modify the default credentials and ip that are supplied to the shell
started by the command "python metapython.py". Near the top of the file
mpre.shell_launcher.py there is an options dictionary. You can set your 
username and/or password here. You can also modify the host_info key if you regularly want to log in to a remote machine.

Exploring the Shell
------------------

Now that you can log in, you can examine some of the differences between this
and the standard CPython shell. Similarly to pythons .startup file for the 
regular interpreter, there is a hook to execute code when the shell is loaded.
This file is called shell_launcher.py and was mentioned previously. If you
enter the metapython shell and enter:

    print dir()
    
You will see the items as defined in shell_launcher.py's definitions attribute.
This is a useful hook to create your own sort of builtins that are only 
available from your command prompt. 

A main feature of the environment is the objects dictionary. Similarly to how
pythons locals and globals methods produce dictionaries that map string names
to python objects, the objects dictionary maps string instance names to 
instances. An objects instance_name is a predictable and obvious string. It 
is simply the name of the type of the object. So for example, the 
instance_name of the mpre._metapython.Metapython object is simply 
"Metapython". 

If there is more then one of that type of object, then each successive name
will have an incremented number appended. So for example, the second
network.Socket you create will have the instance_name "Socket1". Note the
number is 1 because of 0 based indexing. 

Base objects are added to mpre.environment and therefore the objects dictionary
automatically. "Regular" python objects can obtain a reference in the objects 
dictionary by instantiating them with the create method.

The combination of instance names and the objects dictionary allows the use of 
objects that do not appear in the current lexical scope. For example, from the 
metapython command line:
    
    >>> _socket = create("socket.socket")
    >>> assert objects["_socketobject"] is _socket
    >>> print "at command line, id: ", id(_socket)
    at command line, id: 39379832
    
Now open up idtest.py in your text editor of choice and put this in it:
        
    import mpre
    print "inside new script, id: ", id(mpre.objects["_socketobject"])
    
Save it, and then back at the still running command line:
        
    >>> import idtest
    inside new script, id: ", 39379832
    
All it requires is that the referenced object must exist. The objects dictionary
is a simple, useful tool for single threaded concurrency. It is also useful in
that from the command line it provides you with the ability to examine or
modify the attributes of objects while the program is running. 

For more help in getting started on writing your application, refer to the
tutorial and from there the documentation and source code. 
