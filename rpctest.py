#enable launching of any number of requests - no waiting queue
#    - secure socket setup handshake
#        - no requests sent until done
#        
#host info to connection lookup
#    hosts dictionary which maps host info to rpc requester
#    
#
        
import mpre
import mpre.networkssl

def packetize_send(send):
    def _send(self, data):
        return send(self, str(len(data)) + ' ' + data)   
    return _send
    
def packetize_recv(recv):
    def _recv(self, buffer_size=0):
        data = recv(self, buffer_size)
        packets = []
        while data:
            try:
                packet_size, data = data.split(' ', 1)
            except ValueError:
                self._old_data = data
                break
            packet_size = int(packet_size)
            packets.append(data[:packet_size])
            data = data[packet_size:]   
        return packets    
    return _recv
    
class Packet_Client(mpre.networkssl.SSL_Client):
            
    defaults = mpre.networkssl.SSL_Client.defaults.copy()
    defaults.update({"_old_data" : bytes()})
    
    @packetize_send
    def send(self, data):
        return super(Packet_Client, self).send(data)
    
    @packetize_recv
    def recv(self, buffer_size=0):
        return super(Packet_Client, self).recv(buffer_size)      
        
        
class Packet_Socket(mpre.networkssl.SSL_Socket):
            
    defaults = mpre.networkssl.SSL_Socket.defaults.copy()
    defaults.update({"_old_data" : bytes()})
    
    @packetize_send
    def send(self, data):
        return super(Packet_Socket, self).send(data)
    
    @packetize_recv
    def recv(self, buffer_size=0):        
        return super(Packet_Socket, self).recv(buffer_size)
                       
            
class Packet_Server(mpre.networkssl.SSL_Server):
    
    defaults = mpre.networkssl.SSL_Server.defaults.copy()
    defaults.update({"Tcp_Socket_type" : Packet_Socket})
        
            
        
class Rpc_Client(Packet_Client):
            
    defaults = Packet_Client.defaults.copy()
        
    def on_ssl_authentication(self):
        for request, callback in self._requests:
            self.send(request)
            self.callbacks.append(callback)       
        
    def make_request(self, request, callback):
        if not self.ssl_authenticated:
            self._requests.append((request, callback))
        else:    
            self.send(request)
            self.callbacks.append(callback)
        
    def recv(self, packet_count=0):
        for response in super(Rpc_Client, self).recv():
            self.callbacks.pop(0)(self.deserealize(response))
            
        
class Rpc_Socket(Packet_Socket):
            
    defaults = Packet_Socket.defaults.copy()
    
    def on_connect(self):
        self._peername = self.getpeername()
        super(Rpc_Socket, self).on_connect()
        
    def recv(self, packet_count=0):
        peername = self._peername
        environment_access = mpre.objects["Environment_Access"]
        security_context = mpre.objects["Security_Context"]
        
        for packet in super(Rpc_Socket, self).recv():
            (channel_session_id, application_session_id, 
             component_name, method, 
             serialized_arguments) = packet.split(' ', 4)
             
            permission = False
            if channel_session_id == '0': 
                if (method in ("register", "login") and 
                    component_name == "Environment_Access"):
                    
                    permission = True
            else:
                security_context.set_context(channel_session_id, _peername)
                if (permission or 
                    environment_access.validate()):
                    
                    security_context.set_context(application_session_id,
                                                 peername)
                    try:
                        args, _kwargs = self.deserealize(serialized_arguments)
                        instance = mpre.objects[component_name]
                        result = getattr(instance, method)(*args, **kwargs)
                    except BaseException as error:
                        self.alert("Error processing request: \n{}",
                                   [error], level=0)
                        result = error
                    response = self.serealize(result)
                    self.send(response)
                    
    def deserealize(self, serialized_arguments):
        return json.loads(serialized_arguments)
        
    def serealize(self, result):
        return json.dumps(result)


class Session(object):
            
    def __init__(self, host_instance_name, session_id):
        self.id = session_id
        self.host = host_instance_name
        
    def execute(self, instruction, callback):
        request = ' '.join(self.id, instruction.component_name,
                           instruction.method, 
                           json.dumps((instruction.args, instruction.kwargs)))
        mpre.objects[self.host].requester.make_request(request, callback)
        
        
class Host(mpre.authentication.Authenticated_Client):
            
    defaults = mpre.authentication.Authenticated_Client.defaults.copy()
    
    def _get_host_info(self):
        return (self.ip, self.port)
    def _set_host_info(self, value):
        self.ip, self.port = value
    host_info = property(host_info)
    
    def __init__(self, **kwargs):
        super(Host, self).__init__(**kwargs)
        host_info = self.host_info
        mpre.hosts[host_info] = self
        self.requester = self.create("mpre.rpc.Rpc_Requester", 
                                     host_info=host_info,).instance_name
        
    def delete(self):
        del mpre.hosts[self.host_info]
        super(Host, self).delete()
        