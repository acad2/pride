import traceback
import pickle

import mpre
import mpre.base
import mpre.network
components = mpre.components

class RPC_Handler(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"servers" : ("mpre.rpc.RPC_Server", )})
    
    def __init__(self, **kwargs):
        super(RPC_Handler, self).__init__(**kwargs)
        for server_type in self.servers:
            self.create(server_type)
            
    def make_request(self, callback, host_info, transport_protocol, component_name, 
                     method, args, kwargs):
        arguments = pickle.dumps((args, kwargs), pickle.HIGHEST_PROTOCOL)
        request = ' '.join((component_name, method, arguments))
        self.create(RPC_Requester, target=host_info, request=request, 
                    callback=callback if callback is not None else self.alert)
 

class RPC_Server(mpre.network.Server):
    
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

        
class RPC_Requester(mpre.network.Tcp_Client):
    
    def save(self):
        return None
        
    def on_connect(self):
        self.send(self.request)
        
    def recv(self, buffer_size=0):
        packet = super(RPC_Requester, self).recv(buffer_size)
        self.callback(pickle.loads(packet))
        self.delete()    
        
 
class RPC_Request(mpre.network.Tcp_Socket):
    
    def save(self):
        return None
        
    def recv(self, buffer_size=0):
        request = super(RPC_Request, self).recv(buffer_size)
        component_name, method, argument_bytestream = request.split(" ", 2)
        server = components["RPC_Server"]
        server.requester_address = self.getpeername()[0]   
        try:
            args, kwargs = pickle.loads(argument_bytestream)
            call = getattr(components[component_name], method)
        #    self.alert("Performing rpc {}.{}", [component_name, method], level=0)
            response = call(*args, **kwargs)
            response = pickle.dumps(response, pickle.HIGHEST_PROTOCOL)
        except BaseException as error:
            response = pickle.dumps(error, pickle.HIGHEST_PROTOCOL)
        self.send(response)
        self.delete()
        server.requester_address = None