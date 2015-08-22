import functools
import traceback
import json
import pickle


import mpre
import mpre.base
import mpre.network
import mpre.networkssl
import mpre.authentication
import mpre.persistence
import mpre.decorators
objects = mpre.objects

default_serializer = pickle

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
 
_local_sockets = {} 
def fast_local_send(send):
    def _send(self, data):
        if self._peername in _local_sockets:
            instance_name = _local_sockets[self._peername]
            mpre.objects[instance_name]._local_data += data
            mpre.objects[instance_name].recv()
        else:
            return send(self, data)
    return _send
    
class Session(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"id" : '0', 
                     "host_info" : tuple()})
    
    def _get_context(self):
        return self.id, self.host_info
    context = property(_get_context)
    
    def __init__(self, session_id, host_info, **kwargs):
        super(Session, self).__init__(**kwargs)
        self.id = session_id
        self.host_info = host_info
         
    def execute(self, instruction, callback):
        request = ' '.join((self.id, instruction.component_name,
                            instruction.method, 
                            default_serializer.dumps((instruction.args, 
                                                      instruction.kwargs))))
        mpre.hosts[self.host_info]._make_request(request, callback)
        
        
class Host(mpre.authentication.Authenticated_Client):
            
    defaults = mpre.authentication.Authenticated_Client.defaults.copy()
    defaults.update({"target_service" : "Environment_Access",
                     "auto_login" : False})
    
    def _get_host_info(self):
        return (self.ip, self.port)
    def _set_host_info(self, value):
        self.ip, self.port = value
    host_info = property(_get_host_info, _set_host_info)
    
    def __init__(self, **kwargs):
        self._delayed_requests = []
        super(Host, self).__init__(**kwargs)
        host_info = self.host_info
        mpre.hosts[host_info] = self
        self.requester = self.create("mpre.rpc.Rpc_Client", 
                                     host_info=host_info)
        self.login()
        
    def delete(self):
        del mpre.hosts[self.host_info]
        super(Host, self).delete()
        
    def _make_request(self, request, callback):
        if not self.session_id:
            return self._delayed_requests.append((request, callback))
        elif self._delayed_requests:
            for _request, _callback in self._delayed_requests:
                self.requester.make_request(self.session_id + ' ' + _request,
                                            _callback)
            self._delayed_requests = None
        self.requester.make_request(self.session_id + ' ' + request, 
                                    callback)         
        
        
class Session_Manager(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"session_id" : '0',
                     "host_info" : tuple()})
    
    def _get_current(self):
        return self.session_id, self.host_info
    def _set_current(self, value):
        self.session_id, self.host_info = value
    current_session = property(_get_current, _set_current)
        
            
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
                       
                        
class Rpc_Server(mpre.networkssl.SSL_Server):
    
    defaults = mpre.networkssl.SSL_Server.defaults.copy()
    defaults.update({"port" : 40022,
                     "interface" : "localhost",
                     "Tcp_Socket_type" : "mpre.rpc.Rpc_Socket"})
    
    
class Rpc_Client(Packet_Client):
            
    defaults = Packet_Client.defaults.copy()
    
    def __init__(self, **kwargs):
        self._requests, self._callbacks = [], []
        super(Rpc_Client, self).__init__(**kwargs)
        
    def on_ssl_authentication(self):
        for request, callback in self._requests:
            self.send(request)
            self._callbacks.append(callback)       
        
    def make_request(self, request, callback):
        if not self.ssl_authenticated:
            self._requests.append((request, callback))
        else:    
            self.send(request)
            self._callbacks.append(callback)
        
    def recv(self, packet_count=0):
        for response in super(Rpc_Client, self).recv():
            _response = self.deserealize(response)
            callback = self._callbacks.pop(0)
            if isinstance(_response, BaseException):
                callback = functools.partial(self.handle_exception, callback)
            callback(_response)
            
    def handle_exception(self, callback, response):
        self.alert("Exception {} from rpc with callback {}",
                   (response, callback), level=0)
        if (isinstance(response, SystemExit) or 
            isinstance(response, KeyboardInterrupt)):
            raise response        
            
    def deserealize(self, response):
        return default_serializer.loads(response)
        
        
class Rpc_Socket(Packet_Socket):
            
    defaults = Packet_Socket.defaults.copy()
    defaults.update({"debug_mode" : True})
    
    def __init__(self, **kwargs):
        super(Rpc_Socket, self).__init__(**kwargs)
        self._peername = self.getpeername()
                
    def recv(self, packet_count=0):
        peername = self._peername
        environment_access = mpre.objects["Environment_Access"]
        session_manager = mpre.objects["Session_Manager"]
        
        for packet in super(Rpc_Socket, self).recv():
            (channel_session_id, application_session_id, 
             component_name, method, 
             serialized_arguments) = packet.split(' ', 4)
            print "\nsession id: ", channel_session_id
            print "application id: ", application_session_id
            print "call: ", component_name, method
            
            permission = False
            if channel_session_id == '0': 
                if (method in ("register", "login") and 
                    component_name == "Environment_Access"):
                    permission = True
            else:
                if not self.sesion_id:
                    self.session_id = channel_session_id
                assert self.sesion_id == channel_session_id
                
            session_manager.current_session = (channel_session_id, peername)
            if (permission or 
                environment_access.validate()):
                print "permission: {}; validated: {}".format(permission, environment_access.validate())
                session_manager.current_session = (application_session_id,
                                                   peername)
                try:
                    args, kwargs = self.deserealize(serialized_arguments)
                    instance = mpre.objects[component_name]
                    self.alert("Calling: {}.{}({}{})".format(instance, method,
                                                             args, kwargs))
                    result = getattr(instance, method)(*args, **kwargs)
                except BaseException as error:
                    self.alert("Error processing request: \n{}",
                               [error], level=0)
                    result = error
            else:
                self.alert("Denied rpc request {}".format(packet))            
                result = mpre.authentication.UnauthorizedError()
            self.send(self.serealize(result))
            
    def deserealize(self, serialized_arguments):
        return default_serializer.loads(serialized_arguments)
        
    def serealize(self, result):
        return default_serializer.dumps(result)

        
class Environment_Access(mpre.authentication.Authenticated_Service):
    
    defaults = mpre.authentication.Authenticated_Service.defaults.copy()
    defaults.update({"allow_registration" : True})
    
    def __init__(self, **kwargs):
        super(Environment_Access, self).__init__(**kwargs)
        self.create("mpre.rpc.Rpc_Server")
        self.create("mpre.rpc.Session_Manager")
        
    @mpre.authentication.whitelisted
    @mpre.authentication.authenticated
    def validate(self):
        # presuming the host info passed the checks done by the above decorators,
        # the host will have permission to use the environment. 
        return True
        
    @mpre.authentication.whitelisted
    def login(self, username, credentials):
        auth_token, host_info = $Session_Manager.current_session
        if (username == "localhost" and 
            host_info[0] not in ("localhost", "127.0.0.1")):
            
            self.alert("Detected login attempt by username 'localhost'" + 
                       "from non local endpoint {}", (host_info, ))
            raise UnauthorizedError()
        return super(Environment_Access, self).login(username, credentials)
        
        
class Environment_Access_Client(mpre.authentication.Authenticated_Client):
    
    defaults = mpre.authentication.Authenticated_Client.defaults.copy()
    defaults.update({"target_service" : "Environment_Access",
                     "username" : "",
                     "password" : ""})             
