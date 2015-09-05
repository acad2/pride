import struct
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
_old_data, _hosts = {}, {}

def packetize_send(send):
    def _send(self, data):
        return send(self, str(len(data)) + ' ' + data)   
    return _send
    
def packetize_recv(recv):
    def _recv(self, buffer_size=0):
        try:
            data = _old_data[self] + recv(self, buffer_size)
        except KeyError:
            data = recv(self, buffer_size)            
        _old_data[self] = ''
        packets = []
        while data:
            try:
                packet_size, data = data.split(' ', 1)
            except ValueError:
                _old_data[self] = data
                break
            packet_size = int(packet_size)
            packets.append(data[:packet_size])
            data = data[packet_size:]   
        return packets    
    return _recv
   
        
class Session(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"id" : '0', 
                     "host_info" : tuple(),
                     "requester_type" : "mpre.rpc.Rpc_Client"})
    
    def _get_id(self):
        return self._id
    def _set_id(self, value):
        self._id = value
        self.id_size = struct.pack('l', len(value))
    id = property(_get_id, _set_id)
    
    def _get_context(self):
        return self.id, self.host_info
    context = property(_get_context)
    
    def _get_callback(self):
        return self._callbacks.pop(0)
    callback = property(_get_callback)
    
    def __init__(self, session_id, host_info, **kwargs):
        self._callbacks = []
        super(Session, self).__init__(**kwargs)
        self.id = session_id
        self.host_info = host_info
         
    def execute(self, instruction, callback):
        request = ' '.join((self.id_size + self.id, 
                            instruction.component_name, instruction.method, 
                            default_serializer.dumps((instruction.args, 
                                                      instruction.kwargs))))
        try:
            host = _hosts[self.host_info]
        except KeyError:
            host = _hosts[self.host_info] = self.create(self.requester_type,
                                                        host_info=self.host_info)
        host.make_request(request, self.instance_name)
        self._callbacks.append(callback)
        
            
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
        count = 1
        length = len(self._requests)
        for request, callback in self._requests:
            self.alert("Making delayed request {}/{}: {}".format(count, length, request)[:128], level='vv')
            self._callbacks.append(callback)  
            self.send(request)
            
    def make_request(self, request, callback_owner):
        if not self.ssl_authenticated:
            self.alert("Delaying request until authenticated: {}".format(request)[:128], level='vv')
            self._requests.append((request, callback_owner))
        else:    
            self.alert("Making request for {}".format(callback_owner), level='v')
            self._callbacks.append(callback_owner)
            self.send(request)            
        
    def recv(self, packet_count=0):
        for response in super(Rpc_Client, self).recv():
            _response = self.deserealize(response)
            callback_owner = self._callbacks.pop(0)
            if isinstance(_response, BaseException):
                self.handle_exception(callback_owner, _response)
            else:    
                try:
                    mpre.objects[callback_owner].callback(_response)
                except KeyError:
                    self.alert("Could not resolve callback_owner '{}' for {} {}",
                               (callback_owner, "callback with arguments {}",
                                _response), level=0)
                except TypeError:
                    pass
                    
    def handle_exception(self, callback_owner, response):
        self.alert("Exception {} from rpc with callback owner {}",
                   (response.traceback, callback_owner), level=0)
        if (isinstance(response, SystemExit) or 
            isinstance(response, KeyboardInterrupt)):
            print "Reraising exception", type(response)()
            raise type(response)()
            
            
    def deserealize(self, response):
        return default_serializer.loads(response)
        
        
class Rpc_Socket(Packet_Socket):
            
    defaults = Packet_Socket.defaults.copy()
    defaults.update({"debug_mode" : True})
    
  #  def __init__(self, **kwargs):
   #     super(Rpc_Socket, self).__init__(**kwargs)
       # self._peername = self.getpeername()
                
    def recv(self, packet_count=0):
        peername = self.peername        
        for packet in super(Rpc_Socket, self).recv():
            session_id_size = struct.unpack('l', packet[:4])[0]
            end_session_id = 4 + session_id_size
            session_id = packet[4:end_session_id]
            (component_name, method, 
             serialized_arguments) = packet[end_session_id + 1:].split(' ', 2)

           # print "\nsession id: ", len(session_id), session_id
           # print "\ninstance: ", component_name
           # print "\nmethod: ", len(method), method
           # print "\narguments: ", serialized_arguments[:128], ' ...'
            
            permission = False
            if session_id == '0': 
                if method in ("register", "login"):
                    permission = True
            try:
                instance = mpre.objects[component_name]
            except KeyError as result:
                pass
            else:
                if (permission or 
                    instance.validate(session_id, peername, method)):
                    instance.current_session = (session_id, peername)
                    try:
                        args, kwargs = self.deserealize(serialized_arguments)
                        result = getattr(instance, method)(*args, **kwargs)
                    except BaseException as result:
                        stack_trace = traceback.format_exc()
                        self.alert("Exception processing request {}.{}: \n{}",
                                   [component_name, method, stack_trace],
                                   level='vv')
                        if isinstance(result, SystemExit):
                            raise                                   
                        result.traceback = stack_trace
                else:
                    self.alert("Denying unauthorized request: {}",
                               (packet, ), level='v')
                    result = mpre.authentication.UnauthorizedError()
            self.alert("Sending result of {}.{}: {}".format(instance, method, result), level='vv')
            self.send(self.serealize(result))
            
    def deserealize(self, serialized_arguments):
        return default_serializer.loads(serialized_arguments)
        
    def serealize(self, result):
        return default_serializer.dumps(result)
