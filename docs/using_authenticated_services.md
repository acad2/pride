Using Authenticated Services
===========
Authenticated services and clients are the portals to securely performing
application logic between remote hosts. The methods of an Authenticated 
Service are publicly available to clients that are logged in to the
service. Authenticated Clients are used to interact with these methods. 

Services work via rpc which itself runs over tls. This provides security 
between remote hosts. One tls secured network connection between machines may 
serve any number of different client/service interactions between those 
machines. Services and clients are designed in a way so as to hide 
completely the socket communication between them so that programmers may focus
exclusively on the application logic.

Authenticated services support user registration and login/off. Allowing user 
registration may be toggled on/off. Services also support ip based white and black 
lists, in addition to a method blacklist.

By default, login is handled by the secure remote password protocol. This is
a step up from the basic iterative hashing schemes used in other applications.
The shared secret from the srp exchange is passed to hkdf to derive session id
numbers upon successful login. The client includes the session id with each 
request it makes.

Authenticated clients have an auto_login flag which defaults to True. If the
username is not yet registered set the auto_login flag to False when creating
the client.

Clients have a session object attribute. Session objects posess an execute
method that accepts an Instruction object as an argument. Additionally, each
call to execute must supply a callback method to handle the return value of the
instruction. Session objects are the lever for interacting with the service
on the other side of the rpc portal. Typically each client method will execute
at least one instruction on the target service. Session objects also hold the
session id number and host information.


Code Example
-------------

    import mpre
    import mpre.authentication
    Instruction = mpre.Instruction
    
    class Message_Server(mpre.authentication.Authenticated_Service):
        
        defaults = mpre.authentication.Authenticated_Service.defaults.copy()
        
        def __init__(self, **kwargs):
            self.messages = {}
            super(Message_Server, self).__init__(**kwargs)
            
        def send_message(self, username, message):
            try:
                self.messages[username].append(message)
            except KeyError:
                self.messages[username] = [message]
            
        def receive_messages(self, username):
            return '\n'.join(self.messages.pop(username, []))
            
            
    class Message_Client(mpre.authentication.Authenticated_Client):
        
        defaults = mpre.authentication.Authenticated_Client.defaults.copy()
        defaults.update({"target_service" : "Message_Server"})
        
        def send_message(self, username, message):
            self.session.execute(Instruction(self.target_service, "send_message",
                                             username, message), None)
                                
        def receive_messages(self):
            self.session.execute(Instruction(self.target_service,
                                             "receive_messages", self.username),
                                self.alert)
                                
    if __name__ == "__main__":
        $Metapython.create("mpre.chattest.Message_Server")
        $Metapython.create("mpre.chattest.Message_Client", auto_login=False,
                            username="test_user")
        if (("test_user", ) not in
             $Message_Server.database.query("Credentials", ("username", ))):
            $Message_Client.register()
        $Message_Client.login()
        $Message_Client.send_message('test_user', "Note to self: Awesome!")
        $Message_Client.receive_messages()
        
In the above we define a messaging service and client. The client sends
messages to a specified username. In this model the client must elect to pull messages from the server via the receive_messages method. Session objects
are used to execute Instruction objects, which is what will start the chain to
call the specified method on the target service.

The main launcher section creates a server and client. If the username 
"test user" is not yet registered in the database, the client attempts to 
register it. Then the client proceeds to login and send a message to itself.

FAQs
------------

Q: How do I create a network service that requires authentication?
    
    A: Subclass the pride.authentication.Authenticated_Service and 
       Authenticated_Client classes
       
Q: How do I control access to authenticated services?

    A: Authenticated services support:
        
        - ip black/whitelisting
            - use the ip_whitelist and ip_blacklist attributes
            - entries in the form of "xxx.xxx.xxx.xxx"
        - method blacklisting
            - use the method_blacklist attribute
            - entries in the form of string method names
        - method rate limiting
            - use the rate_limit inherited attribute
            - rate_limit maps method name to minimum time interval that the
              name method can be called (1 call every x seconds)
            - login and registration default to 1 call every 2 seconds
        - allow_login and allow_registration flags
            - enable or disable login and registration
        - the validate method determines permission for the specified request
            - can be extended or overloaded to fine tune permissions given the
              current sesion id, host info, and method name
              
Q: How do I interact with authenticated services?

    A: Authenticated_Client objects come with the appropriate boilerplate code
       for working with registration/logging in to authenticated services.
       
       - use the session attribute and it's execute method to execute Instructions
         remotely
         
Q: What kind of security protects remote object access?

    A: Communication between machines is secured via tls. This in itself does
       not control access to sensitive services. Authenticated services and
       clients support user registration and login. Login is negotiated via
       the secure remote password protocol and a cryptographic session identifier
       is generated from the resultant secret. Current no additional security
       measures are applied to network data (no redundant encryption or MAC).
       
       Remote procedure call sockets are programmed to decline any request to
       objects that do not possess a validate method. Access to arbitrary 
       objects can be obtained through the Shell and Interpreter.