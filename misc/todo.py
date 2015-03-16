import mpre.network as network
import mpre.defaults as defaults

class Tcp_Service_Proxy(network.Server):

    def __init__(self, **kwargs):
        super(Tcp_Service_Proxy, self).__init__(**kwargs)
        self.Tcp_Socket_type = Proxy_Client
                
    def on_connect(self, connection):
        pass
        
        
class Proxy_Client(network.Tcp_Socket):
    
    def __init__(self, **kwargs):
        super(Proxy_Client, self).__init__(**kwargs)
        
    def recv(self):
        request = self.wrapped_object.recv(self.network_packet_size)        
        service_name, command, value = request.split(" ", 2)
        self.respond_with(self.reply)
        request = command + " " + value
        self.reaction(service_name, request)
              
    def reply(self, sender, packet):
        self.send(str(sender) + " " + packet)

                           
"""
class Tcp_Service_Test(network.Tcp_Client):
    
    def on_connect(self):        
        self.send("File_Service get_filesize base.py")
                           
    def recv(self):
        self.network_buffer += self.socket.recv(self.network_packet_size)
"""

class Pyobject_Reactor(mpre.base.Reactor):
    
    defaults = mpre.defaults.Reactor.copy()
    
    def __init__(self, **kwargs):
        super(Pyobject_Reactor, self).__init__(**kwargs)
        
    def pyobject_method(self, sender, packet):
        component, method, argument_info = packet.split(" ", 2)
        argument_dictionary = pickle.loads(argument_info)
        
        
layer_map = {(x, [cached_layer, draw_method]) for x in xrange(60)}

renderer.blit(layer_map[cached_layer_level][0]
for layer in xrange(cached_layer_level + 1, max_layers):
    renderer.blit(layer_however)
        