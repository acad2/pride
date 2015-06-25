import traceback
import pickle

import mpre
import mpre.base
import mpre.network
import mpre.networkssl
import mpre.persistence
objects = mpre.objects

class RPC_Handler(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"servers" : {"Tcp" : "mpre.rpc.RPC_Server"},
                     "current_connections" : None})
    
    def __init__(self, **kwargs):
        super(RPC_Handler, self).__init__(**kwargs)
        self.current_connections = self.current_connections or {}
        
        for server_protocol, server_type in self.servers.items():
            setattr(self, "{}_server".format(server_protocol), self.create(server_type))
            
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
 

class RPC_Server(mpre.networkssl.SSL_Server):
    
    defaults = mpre.network.Server.defaults.copy()
    defaults.update({"port" : 40022,
                     "interface" : "localhost",
                     "Tcp_Socket_type" : "mpre.rpc.RPC_Request"})
        
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
        self._callbacks = []
        super(RPC_Requester, self).__init__(**kwargs)
                
    def __getstate__(self):
        state = super(RPC_Requester, self).__getstate__()
        state["callback"] = mpre.persistence.save_function(state["callback"])
        return state
        
    def on_authentication(self):
        self.make_request(self.callback, self.request)
    
    def make_request(self, callback, request):
        self.send(request)
        self._callbacks.append(callback)
        
    def recv(self, buffer_size=0):
        packet = super(RPC_Requester, self).recv(buffer_size)
        callback = self._callbacks.pop(0)
        callback(pickle.loads(packet))
                
 
class RPC_Request(mpre.networkssl.SSL_Socket):
    
    defaults = mpre.networkssl.SSL_Socket.defaults.copy()
    defaults.update({"dont_save" : True,
                     "rpc_verbosity" : 'v'})
   
    def recv(self, buffer_size=0):
        request = super(RPC_Request, self).recv(buffer_size)
        component_name, method, argument_bytestream = request.split(" ", 2)
        instance = objects[component_name]
        instance.requester_address = self.getpeername()[0]   
        try:
            args, kwargs = pickle.loads(argument_bytestream)
            call = getattr(instance, method)
            self.alert("Executing {}.{}", [component_name, method], level=self.rpc_verbosity)
            response = call(*args, **kwargs)
            response = pickle.dumps(response, pickle.HIGHEST_PROTOCOL)
        except BaseException as error:
            self.alert("Exception executing {}.{}", [component_name, method], level='v')
            response = pickle.dumps(error, pickle.HIGHEST_PROTOCOL)
        instance.requester_address = None
        self.send(response)     