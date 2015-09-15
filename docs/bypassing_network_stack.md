Bypassing the network stack
-------------
Instance names allow interaction with a specific object, given that the instance
name can be acquired. Socket objects have instance names. Thus two endpoints that 
exist within the same application process can use instance names to call the
send/recv methods, bypassing the network stack completely and performing the 
operation inline. Because of the callback oriented nature of rpc and the
centralized portal it provides, a complete conversation (i.e. a multi stage 
login) can happen inline. This saves several back and forths over the 
loopback connector. 

For the specific implementation details, please view the network module source.
