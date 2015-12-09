Secure Remote Objects
----------------
Pride offers secure, authenticated, remote access to python objects. Arbitrary
objects may be accessed through the Interpreter via the Shell. Otherwise
only objects that subclass from pride.authentication.Authenticated_Service
will be reachable from the remote procedure call portal. Authenticated Service
objects are not themselves networked and have no interaction with sockets,
servers, or sending or receiving data. A single server services all remote
procedure calls regardless of which authenticated service is being used, or
how many. 

Access to an authenticated service requires login (with prior registration). 
Both registration and login can be disabled via the allow_registration and 
allow_login attributes. 

Access to authenticated services can be controlled via ip white listing,
black listing, and method name blacklisting. Besides this generic controls,
subclasses may override or extend the validate method to implement whatever
access controls are desired. 

Communication between hosts is secured by tls at the socket layer and 
additionally by authenticated services at the application layer. Authenticated
services negotiate a shared secret with the client via the secure remote password
protocol. This secret is used to derive a session identifier via the hmac based
extract and expand key derivation function (hkdf). Currently no additional 
encryption is implemented on top of that performed by tls.

Secure and sensitive services are recommended to set the allow_registration 
flag to False and negotiate registration through an out of band channel. 
Credentials may be added to the database directly through the database objects
with their associated api or by running the registration program in
pride.programs locally on the server.

Authenticated_Client objects are used to interface with authenticated 
services. Upon initialization a Session object is created. This object
manages the session id and has an execute method. This method accepts 
Instruction objects and a callback for arguments. The supplied instruction
is executed remotely (if authorized) and the return result supplied as the
argument to callback. In the event the request generates an exception, the
callback will be discarded.