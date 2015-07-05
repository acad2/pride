import traceback
import pickle

import mpre
import mpre.base
import mpre.network
import mpre.networkssl
import mpre.authentication
import mpre.persistence
objects = mpre.objects


class Machine_Access(mpre.authentication.Authenticated_Service):
    
    defaults = mpre.authentication.Authenticated_Service.defaults.copy()
    defaults.update({"allow_registration" : True,
                     "certfile" : "Machine_Access",
                     "keyfile" : "Machine_Access"})
    

class Machine_Access_Client(mpre.authentication.Authenticated_Client):
    
    defaults = mpre.authentication.Authenticated_Client.defaults.copy()
    defaults.update({"target_service" : "Machine_Access",
                     "username" : "root",
                     "password" : "password"})
    
    
class RPC_Handler(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"servers" : {"tcp" : "mpre.rpc.RPC_Server"},
                     "current_connections" : None,
                     "require_machine_access" : True,
                     "remote_hosts" : (("localhost", 40022), )})
    
    def __init__(self, **kwargs):
        super(RPC_Handler, self).__init__(**kwargs)
        self.current_connections = self.current_connections or {}
        
        if self.require_machine_access:
            self.create(Machine_Access)
            
        for server_protocol, server_type in self.servers.items():
            setattr(self, "{}_server".format(server_protocol), self.create(server_type))
            
        for host_info in self.remote_hosts:
            self.create(Machine_Access_Client, host_info=host_info)
                                        
    def make_request(self, callback, host_info, transport_protocol, component_name, 
                     method, args, kwargs):
        arguments = pickle.dumps((args, kwargs), pickle.HIGHEST_PROTOCOL)
        request = ' '.join((component_name, method, arguments))
        if host_info in self.current_connections:
            requester = self.current_connections[host_info]
            requester.make_request(callback, request)
        else:
            server = getattr(self, "{}_server".format(transport_protocol))
            connection = server.create(RPC_Requester, target=host_info, 
                                       request=request, callback=callback if callback else self.alert)
            
            self.current_connections[host_info] = connection
 
    def delete(self):
        for connection in self.current_connections.values():
            connection.close()
        super(RPC_Handler, self).delete()
        
    def __getstate__(self):
        state = super(RPC_Handler, self).__getstate__()
        state["current_connections"] = {}
        return state
            
        
class RPC_Server(mpre.networkssl.SSL_Server):
    
    defaults = mpre.networkssl.SSL_Server.defaults.copy()
    defaults.update({"port" : 40022,
                     "interface" : "localhost",
                     "Tcp_Socket_type" : "mpre.rpc.RPC_Request",
                     "require_machine_access" : True})
        
    def __init__(self, **kwargs):
        super(RPC_Server, self).__init__(**kwargs)
        
    def __getstate__(self):
        attributes = super(RPC_Server, self).__getstate__()
        attributes["objects"] = {}
        
        return attributes

    
class RPC_Requester(mpre.networkssl.SSL_Client):
    
    defaults = mpre.networkssl.SSL_Client.defaults.copy()
    defaults.update({"dont_save" : True})
    
    def __init__(self, **kwargs):
        self._requests, self._callbacks = [], []
        super(RPC_Requester, self).__init__(**kwargs)
                
    def __getstate__(self):
        state = super(RPC_Requester, self).__getstate__()
        state["callback"] = mpre.persistence.save_function(state["callback"])
        return state
        
    def on_authentication(self):
        self.send(self.request)
    
    def make_request(self, callback, request):
        if not self.callback and self.ssl_authenticated:
            self.callback = callback
            #self.alert("Making request: {}".format(request[:128]), level=0)
            self.send(request)
        else:
            #self.alert("Delaying request: {}".format(request[:128]), level=0)
            self._requests.append((callback, request))
        
    def recv(self, buffer_size=0):
        packet = super(RPC_Requester, self).recv(buffer_size)
        arguments = pickle.loads(packet)
        callback = self.callback
        self.callback = None
        if isinstance(arguments, BaseException):
            if type(arguments) in (KeyboardInterrupt, SystemExit):
                raise arguments
            
            self.alert("{}: {} when performing last request", 
                       (type(arguments), arguments), level=0)
        else:
            if not callback:
                if arguments:
                    self.alert("received reply: {}".format(arguments))
            else:
                callback(arguments)
        
        if not self.callback and self._requests:       
            self.callback, request = self._requests.pop(0)
            self.send(request)                
                
 
class RPC_Request(mpre.networkssl.SSL_Socket):
    
    defaults = mpre.networkssl.SSL_Socket.defaults.copy()
    defaults.update({"dont_save" : True,
                     "rpc_verbosity" : 'vv',
                     "certfile" : "server.crt",
                     "keyfile" : "server.key"})
   
    verbosity = {"execution" : 'vv',
                 "exception" : 0}
                 
    def recv(self, buffer_size=0):
        request = super(RPC_Request, self).recv(buffer_size)
        component_name, method, argument_bytestream = request.split(" ", 2)
        instance = objects[component_name]
        instance.requester_address = self.getpeername()[0]   
        if (component_name != "Machine_Access" and
            instance.requester_address not in objects["Machine_Access"].logged_in):
            response = pickle.dumps(mpre.authentication.UnauthorizedError())
        else:
            try:
                args, kwargs = pickle.loads(argument_bytestream)
                call = getattr(instance, method)
                self.alert("Executing {}.{}", [component_name, method], 
                           level=self.verbosity["execution"])
                response = pickle.dumps(call(*args, **kwargs))
            except BaseException as error:
                if not isinstance(error, SystemExit):
                    self.alert("Exception when executing {}.{}\n{}", [component_name, method, error], 
                               level=self.verbosity["exception"])
                response = pickle.dumps(error, pickle.HIGHEST_PROTOCOL)
        instance.requester_address = None
        self.send(response)     
        

#class Signed_Request(mpre.networkssl.SSL_Socket):
#    
#    def recv(self, buffer_size=0):
#        request = super(Signed_Request, self).recv(buffer_size)       