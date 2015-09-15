Using Authenticated Services
===========
Authenticated services and clients are the portals to securely performing
application logic between remote hosts. The methods of an Authenticated 
Service are publicly available to hosts that are logged in to the
service. Authenticated Clients are used to interact with these methods. 
Authenticated services support user registration and login/off. Allowing user 
registration may be toggled. Services also support ip based white and black 
lists, in addition to a method blacklist. 

By default, login is handled by the secure remote password protocol. This is
a step up from the basic iterative hashing schemes used in many other areas.
Note that services work via rpc which itself runs over tls. This provides
security between the machines. Because one network connection between 
machines may serve any number of different client/service conn