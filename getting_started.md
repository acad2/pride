Getting Started
---------------

Two things need to be done before you can get started. Remote procedure calls are
done over ssl and ssl servers require certificates. You can generate a self
signed certificate via running the command:
    
    python ./programs/create_self_signed_certificate.py
    
This will generate the required server.crt, server.csr, and server.key files needed.
Note that you can generate files by other names through the --name keyword, though
for ease of configuration here we will go with the default.

The second thing you will need to do is register an account. An account currently 
consists of a username and a password. In the mpre.programs package there is a file 
called register.py.

If you are registering with a remote machine, you will need a Environment_Access account.
This allows you to make remote procedure calls to any object that has a reference
in the environment. This is not required for the local machine. Run this command:

    python metapython.py ./programs/register.py --client_name mpre.rpc.Environment_Access_Client [--ip]
    
To obtain access to the command line shell, Run the following command:

    python metapython.py ./programs/register.py --client_name mpre._metapython.Shell [--ip]
    
Note that the ip argument is optional and only needs to be specified when registering
with a remote machine.
        
You will be prompted for a username and a password for each each registration. When
offered to login, decline and press ctrl-c to get back to your regular shell. 

You are now setup to use the interactive interpreter. Run the following command:
    
    python metapython.py --username your_username_here
    
You will be prompted for your password. Shortly after you should see the login greeting
and the command prompt. Note that it is possible to supply your password via the
--password argument on the command line, though this is obviously less secure.

If you do not specify a username, a default will be used. You can modify the default 
username and/or password by editing the file shell_launcher.py. Near the top there is 
an options dictionary. You can set your username and password there. You can also
modify the 'ip' key if you want to log in to a remote machine by default.

Exploring the Shell
------------------

Now that you are logged in, you can examine some of the differences between this
and the standard CPython shell. Similarly to pythons .startup file for the regular
interpreter, there is a hook to execute code when this shell is loaded. This file
is called shell_launcher.py and was mentioned previously. If you enter the metapython
shell and enter:

    print dir()
    
You will see the items as defined in shell_launcher.py's definitions attribute. This
is a useful hook to create your own sort of builtins that are only available from
your command prompt. 

A main feature of the environment is the objects dictionary. Similarly to how pythons
locals and globals methods produce dictionaries that map string names to python objects,
the objects dictionary maps string instance names to instances of objects. An objects 
instance_name is a predictable and obvious string. It is simply the name of the type of 
the object. So for example, the instance_name of the mpre._metapython.Metapython object is simply
"Metapython". If there is more then one of that type of object, then each successive 
name will have an incremented number appended. So for example, the third network.Socket 
you create will have the instance_name "Socket2". Note the number is 2 because of 0 based 
indexing.

Base objects have an instance name and are added to mpre.environment and the objects dictionary
automatically. Objects that inherit from the builtin object type can obtain a reference in the 
objects dictionary by instantiation via the create method. To acquire the instance name of such
an object, look up the instance in mpre.environment.instance_names.

The combination of instance names and the objects dictionary allows the use of 
objects that do not appear in the current lexical scope. For example, from the 
metapython command line:
    
    >>> _socket = create("socket.socket")
    >>> assert objects["_socketobject"] is _socket
    >>> print "at command line, id: ", id(_socket)
    at command line, id: 39379832
    
Now open up idtest.py in your text editor of choice and put this in it:
        
    import socket
    import mpre    
    
    _socket = mpre.objects["_socketobject"]
    print "inside new script, id: ", id(_socket)
    _socket.connect(socket.gethostbyname("google.com"), 80)
    
Save it, and then back at the still running command line:
    
    >>> import idtest
    inside new script, id: ", 39379832
    >>> print _socket.getpeername()
    ('74.125.239.37', 80)
    
All it requires is that the referenced object must exist. The objects dictionary
is a simple, useful tool for single threaded concurrency. It is also useful in that
from the command line it provides you with the ability to examine or modify the
attributes of objects while the program is running. 

For more help in getting started on writing your application, refer to the base_tutorial and
from there the documentation and source code. 