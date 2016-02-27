""" pride.rpc - Remote Procedure Call portal built on top of pride.networkssl ssl sockets. """
import struct
import traceback
import itertools
import time

import pride
import pride.base
import pride.utilities
import pride.networkssl
#objects = pride.objects

DEFAULT_SERIALIZER = type("Serializer", (object, ), {"dumps" : staticmethod(pride.utilities.save_data),
                                                     "loads" : staticmethod(pride.utilities.load_data)})
_old_data, _hosts = {}, {}

class UnauthorizedError(Warning): pass  

def packetize_send(send):
    """ Decorator that transforms a tcp stream into packets. Requires the use
        of the packetize_recv decorator on the recv end. """
    def _send(self, data):
        return send(self, str(len(data)) + ' ' + data)   
    return _send
    
def packetize_recv(recv):
    """ Decorator that breaks a tcp stream into packets based on packet sizes,
        as supplied by the corresponding packetize_send decorator. In the event
        less then an entire packet is received, the received data is stored 
        until the remainder is received.
        
        The recv method decorated by this function will return a list of
        packets received or an empty list if no complete packets have been
        received. """        
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
   
        
class Session(pride.base.Base):
    """ Maintains session id information and prepares outgoing requests """
    defaults = {"requester_type" : "pride.rpc.Rpc_Client"}
    
    def _get_id(self):
        return self._id
    def _set_id(self, value):
        self._id = value
        self.id_size = struct.pack('l', len(value))
    id = property(_get_id, _set_id)
    
    def _get_context(self):
        return self.id, self.host_info
    context = property(_get_context)
    
    def __init__(self, session_id, host_info, **kwargs):
        self._callbacks = []
        super(Session, self).__init__(**kwargs)
        self.id = session_id
        self.host_info = host_info
                
    def execute(self, instruction, callback):
        """ Prepare instruction as a request to be sent by an Rpc_Client. A 
            request consists of session id information (size and id#), 
            followed by the information from the supplied instruction. No
            information regarding the callback is included in the request. """
        _call = component, method = instruction.component_name, instruction.method
        #print "Pickling: ", instruction.args, instruction.kwargs
        request = pride.utilities.save_data(self.id, component, method, 
                                            DEFAULT_SERIALIZER.dumps((instruction.args, 
                                                                      instruction.kwargs)))
        host = pride.objects["->Python->Rpc_Connection_Manager"].get_host(self.host_info) 
        # we have to insert at the beginning things will happen inline, and
        # must append to the end when network round trips with callbacks are used
        if host.bypass_network_stack and host._endpoint_reference:
            self._callbacks.insert(0, (_call, callback))    
        else:
            self._callbacks.append((_call, callback))
        host.make_request(request, self.reference)
       
    def next_callback(self):      
        return self._callbacks.pop(0)
                
        
class Packet_Client(pride.networkssl.SSL_Client):
    """ An SSL_Client that uses packetized send and recv (client side) """        
    defaults = {"_old_data" : bytes()}
    
    @packetize_send
    def send(self, data):
        return super(Packet_Client, self).send(data)
    
    @packetize_recv
    def recv(self, buffer_size=0):
        return super(Packet_Client, self).recv(buffer_size)      
        
        
class Packet_Socket(pride.networkssl.SSL_Socket):
    """ An SSL_Socket that uses packetized send and recv (server side) """        
    defaults = {"_old_data" : bytes()}
    
    @packetize_send
    def send(self, data):
        return super(Packet_Socket, self).send(data)
    
    @packetize_recv
    def recv(self, buffer_size=0):        
        return super(Packet_Socket, self).recv(buffer_size)
                       
                        
class Rpc_Connection_Manager(pride.base.Base):
    """ Creates Rpc_Clients for making rpc requests. Used to facilitate the
        the usage of a single connection for arbitrary requests to the host. """
    defaults = {"requester_type" : "pride.rpc.Rpc_Client"}
    mutable_defaults = {"hosts" : dict}
    
    def get_host(self, host_info):
        try:
            return self.hosts[host_info]
        except KeyError:
            if host_info in self.hosts:
                raise            
            host = self.hosts[host_info] = self.create(self.requester_type, host_info=host_info)  
            return host
    
    def add(self, _object):
        self.hosts[_object.host_info] = _object
        super(Rpc_Connection_Manager, self).add(_object)
        
    def remove(self, _object):
        super(Rpc_Connection_Manager, self).remove(_object)
        del self.hosts[_object.host_info]
        
    def __getstate__(self):
        attributes = super(Rpc_Connection_Manager, self).__getstate__()
        attributes["hosts"] = {}
        return attributes
        
        
class Rpc_Server(pride.networkssl.SSL_Server):
    """ Creates Rpc_Sockets for handling rpc requests. By default, this
        server runs on the localhost only, meaning it is not accessible 
        from the network. """
    defaults = {"port" : 40022, "interface" : "localhost",
                "Tcp_Socket_type" : "pride.rpc.Rpc_Socket"}
        
        
class Rpc_Client(Packet_Client):
    """ Client socket for making rpc requests using packetized tcp stream. """  
    verbosity = {"delayed_request_sent" : "vv", "request_delayed" : "vv",
                 "request_sent" : "vv", "unresolved_callback" : 0, "handle_exception" : 0}
                 
    def __init__(self, **kwargs):
        self._requests, self._callbacks = [], []
        super(Rpc_Client, self).__init__(**kwargs)
        
    def on_ssl_authentication(self):
        count = 1
        length = len(self._requests)
        for request, callback in self._requests:
            self.alert("Making delayed request {}/{}: {}".format(count, length, request)[:128], 
                       level=self.verbosity["delayed_request_sent"])
            self._callbacks.append(callback)  
            self.send(request)
            
    def make_request(self, request, callback_owner):
        """ Send request to remote host and queue callback_owner for callback """
        if not self.ssl_authenticated:
            self.alert("Delaying request until authenticated: {}".format(request)[:128], 
                       level=self.verbosity["request_delayed"])
            self._requests.append((request, callback_owner))
        else:    
            self.alert("Making request for {}".format(callback_owner), level=self.verbosity["request_sent"])
            if self.bypass_network_stack and self._endpoint_reference:
                self._callbacks.insert(0, callback_owner)
            else:
                self._callbacks.append(callback_owner)
            self.send(request)            
        
    def recv(self, packet_count=0):
        for response in super(Rpc_Client, self).recv():         
            _response = self.deserealize(response)
            callback_owner = self._callbacks.pop(0)    
            try:
                _call, callback = pride.objects[callback_owner].next_callback()
            except KeyError:
                self.alert("Could not resolve callback_owner '{}' for {} {}",
                           (callback_owner, "callback with arguments {}",
                            _response), level=self.verbosity["unresolved_callback"])
            else:
                if isinstance(_response, BaseException):
                    self.handle_exception(_call, callback, _response)
                elif callback is not None:                    
                    callback(_response)                                
                                                
    def handle_exception(self, _call, callback, response):   
        if (isinstance(response, SystemExit) or 
            isinstance(response, KeyboardInterrupt)):            
            raise response
        else:
            self.alert("\nRemote Traceback: Exception calling {}\n{}: {}\nUnable to proceed with callback {}",
                       ('.'.join(_call), response.__class__.__name__, 
                        getattr(response, "traceback", response), callback), 
                        level=self.verbosity["handle_exception"])            
            
    def deserealize(self, response):
        return DEFAULT_SERIALIZER.loads(response)
        
        
class Rpc_Socket(Packet_Socket):
    """ Packetized tcp socket for receiving and delegating rpc requests """
    
    defaults = {"idle_after" : 600}
    verbosity = {"request_exception" : 0, "request_result" : "vv"}
        
    def __init__(self, **kwargs):
        super(Rpc_Socket, self).__init__(**kwargs)
        self.rpc_workers = itertools.cycle(objects["->Python"].objects["Rpc_Worker"])
        
    def on_ssl_authentication(self):
        if self.idle_after:
            self._idle_timer = time.time()
            pride.Instruction(self.reference, "check_idle").execute(priority=self.idle_after)
        return super(Rpc_Socket, self).on_ssl_authentication()
        
    def check_idle(self):
        if time.time() - self._idle_timer >= self.idle_after:            
            self.delete()
        else:            
            pride.Instruction(self.reference, "check_idle").execute(priority=self.idle_after)
            
    def recv(self, packet_count=0):
        peername = self.peername
        for (session_id, component_name, method, 
             serialized_arguments) in (pride.utilities.load_data(packet) for 
                                       packet in super(Rpc_Socket, self).recv()):          
            try:
                result = next(self.rpc_workers).handle_request(peername, session_id, component_name,
                                                               method, serialized_arguments)                                    
            except BaseException as result:
                if ((isinstance(result, KeyError) and component_name not in pride.objects) or
                    (isinstance(result, AttributeError) and not hasattr(objects[component_name], "validate"))):
                    result = UnauthorizedError()                
                elif not isinstance(result, UnauthorizedError):
                    stack_trace = traceback.format_exc()
                    result.traceback = stack_trace  
                    if not isinstance(result, SystemExit):
                        self.alert("Exception processing request {}.{}: \n{}",
                                   [component_name, method, stack_trace],
                                   level=self.verbosity["request_exception"])                    
            else:                
                self.alert("Sending result of {}.{}: {}",
                           (component_name, method, result), 
                           level=self.verbosity["request_result"])               
                           
            self.send(self.serialize(result))
      
    def serialize(self, result):
        return DEFAULT_SERIALIZER.dumps(result)  

        
class Rpc_Worker(pride.base.Base):
    """ Performs remote procedure call requests """
    verbosity = {"request_result" : "vvv"}
                 
    def handle_request(self, peername, session_id, component_name, method,
                       serialized_arguments): 
        instance = pride.objects[component_name]
        if not instance.validate(session_id, peername, method):            
            raise UnauthorizedError()
        else:            
            args, kwargs = self.deserealize(serialized_arguments)
            with pride.contextmanagers.backup(instance, "current_session"):
                instance.current_session = (session_id, peername)
                return getattr(instance, method)(*args, **kwargs) 
        
    def deserealize(self, serialized_arguments):
        return DEFAULT_SERIALIZER.loads(serialized_arguments)        