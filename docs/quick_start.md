Quick Start Guide
-----------------
pride offers a secure python shell that requires registration before usage.
When you first run "python main.py" you will be prompted for a username and
password. Entering a currently nonexistant username will automatically
prompt you for registration.

After you register a username, you may want to customize your site_config file.
This file can be used to lay out the defaults for any pride.base.Base object.
Inside site_config.py there is a placeholder that looks like this:

    pride_user_User_defaults = {"username" : ""}
    
If you desire you can enter your username here; If so you will no longer be prompted
for it when logging in. You may do the same with your password; however this is 
not generally advisable. Your password also protects any encrypted files you
save in your user file system, and access to all other application clients 
associated with your user. For more information on the security model, please
consult the documentation/source for pride.user and pride.authentication2.


Headless Programs
-----------------
If you want to use pride to create a program that does not require a graphical
or network frontend, you will start with pride.base.Base. This module contains
prides alternative to the builtin python object type. Base objects have most
standard programming boilerplate code handled programmatically. Simply
create a subclass of pride.base.Base and start writing your application logic.
For an example of the features of Base objects and the differences in how they
are used from standard python objects, see the documentation for pride.base

Here's a small example of a program that unzips .zip files:

    import zipfile
    import pride.base
    
    class Unzipper(pride.base.Base):
        
        defaults = {"filename" : '', "target_directory" : ''}
        required_attributes = ("filename", )
                    
        def __init__(self, **kwargs):
            super(Unzipper, self).__init__(**kwargs)
            with zipfile.ZipFile(self.filename, 'r') as zipped_file:
                if self.target_directory:
                    zipped_file.extractall(self.target_directory)
                else:
                    zipped_file.extractall()
                    
    if __name__ == "__main__":
        zip_file = Unzipper(parse_args=True)
        zip_file.unzip()

Note the parse_args flag specified to the constructor. Command line arguments will
automatically be derived from a Base objects class defaults. If the user who
runs the file does not specify --filename on the command line, the script wil
exit with ValueError, as a required attribute was not specified. These are
some examples of how pride handles the boilerplate code of common tasks.

If you already have significant amounts of code written in another framework,
you may not have much work to do to integrate/update. The pride.base.Wrapper 
object can turn any python object into a Base object, and can be useful for 
patching old objects into pride applications. 


Secure Network Services
------------------
pride offers a secured remote procedure call server that separates the socket
networking layer from the applications that utilize it for data transportation.
Authenticated Services that utilize rpc are usually considerably simpler to 
design. Take for example, this fully functional messenger client/server:

    import pride.authentication2
    
    class Messenger_Client(pride.authentication2.Authenticated_Client):
        
        defaults = {"target_service" : "->Python->Messenger_Service"}
        verbosity = {"send_message" : "vv"}
        
        @pride.authentication2.remote_procedure_call(callback_name="receive_messages")
        def send_message(self, receiver, message): pass
            
        def receive_messages(self, messages):
            for sender, message in messages:
                self.alert("{}: {}", (sender, message), level=self.verbosity.get(sender, 0))
                
                
    class Messenger_Service(pride.authentication2.Authenticated_Service):
                
        mutable_defaults = {"messages" : dict}
        remotely_available_procedures = ("send_message", )
        
        def send_message(self, receiver, message):
            sender = self.session_id[self.current_session[0]]
            if receiver:
                try:
                    self.messages[receiver].append((sender, message))
                except KeyError:
                    self.messages[receiver] = [(sender, message)]
            else:
                self.alert("Sending messages back to: {}", (sender, ), level=0)
            return self.messages.pop(sender, tuple())
            
This, and all other network services, uses tls to secure communications between
client/server. In addition, all services require individual authentication of
the client to the server before any access to the available methods is granted. 

Developing a network service is very similar to developing a non networked
service. For more information, consult the documentation/source of pride.authentication2.


Socket Networking
---------------
If you're really sure that you want to work directly with sockets, i.e. you are
developing a simple network application that requires no authentication, then the
pride.network module is where you can begin. It features asynchronous, callback
oriented socket objects, and slightly higher level abstractions on top, such
as Tcp Client sockets and Udp Multicasters. In general, you will extend the
on_connect and recv methods to implement your application functionality.

Note that network.Socket objects are designed for speed by default. The
default recv and recvfrom utilize recv_into and recvfrom_into, which makes
receiving of data potentially significantly faster, due to how python handles
strings. In addition, sockets that are connected locally to other endpoints 
within the same pride process will bypass the network stack completely, and the
entire chain of send/recv calls will occur inline. This greatly reduces the 
latency of local clients connected to rpc services.


GUI Programming
---------------
pride has support for gui programs, using SDL2 as the backend. The pride
gui toolkit is, as of 1/4/2016, not completely developed. It is certainly
usable, but certain changes may still need to be made to the core rendering
routines (i.e. to facilitate scrolling). For examples, please consult the
pride.gui package and the source files contained therein.


As a (remote) shell service
---------------
As previously mentioned, pride features an rpc portal and a python shell that
runs over it. By default, the rpc portal only runs on the localhost. This
can be changed via the site config to run on all interfaces at any desired port
(the default is 40022). By doing so, your machine can accept remote shell
connections from users who are registered. Registration and login can be 
allowed and disallowed by modifying the site_config file appropriately.
