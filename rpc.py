import traceback
import pickle

import mpre
import mpre.base
import mpre.network
import mpre.networkssl
import mpre.authentication
import mpre.persistence
objects = mpre.objects

class Security_Context(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"authorization_token" : '',
                     "host_info" : tuple()})
        
    def set_context(self, authorization_token, host_info):
        self.authorization_token = authorization_token
        self.host_info = host_info
       
    def get_context(self):
        return self.authorization_token, self.host_info
        
        
class Environment_Access(mpre.authentication.Authenticated_Service):
    
    defaults = mpre.authentication.Authenticated_Service.defaults.copy()
    defaults.update({"allow_registration" : True})
    
    @mpre.authentication.whitelisted
    @mpre.authentication.authenticated
    def validate(self):
        # presuming the host info passed the checks done by the above decorators,
        # the host will have permission to use the environment. 
        return True
        
    @mpre.authentication.whitelisted
    def login(self, username, credentials):
        auth_token, host_info = $Security_Context.get_context()
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
    
    
class RPC_Handler(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"servers" : {"tcp" : "mpre.rpc.RPC_Server"},
                     "current_connections" : None,
                     "require_environment_access" : True,
                     "environment_access_client_type" : "mpre.rpc.Environment_Access_Client",
                     "remote_hosts" : tuple()}) # remote_hosts is (host_info, options_dict)
    
    def __init__(self, **kwargs):
        super(RPC_Handler, self).__init__(**kwargs)
        self.create("mpre.rpc.Security_Context")
        self.current_connections = self.current_connections or {}
        require_environment_access = self.require_environment_access
        if require_environment_access:
            self.create(Environment_Access)
            
        for server_protocol, server_type in self.servers.items():
            setattr(self, "{}_server".format(server_protocol), 
                    self.create(server_type).instance_name)
            
        for host_info, options in self.remote_hosts:
            options = {} if options is None else options
            self.create(self.environment_access_client_type, host_info=host_info, **options)
                                        
    def make_request(self, callback, host_info, transport_protocol,
                     priority_flag, component_name, method, args, kwargs):
        arguments = pickle.dumps((args, kwargs), pickle.HIGHEST_PROTOCOL)
        request = ' '.join((component_name, method, arguments))        
        try:
            connection = self.current_connections[host_info]
        except KeyError:
            server = mpre.objects[getattr(self, 
                                          "{}_server".format(transport_protocol))]
            connection = server.create(RPC_Requester, target=host_info)  
            self.current_connections[host_info] = connection
        connection.make_request(callback, request, priority_flag)            
 
    def delete(self):
        for connection in self.current_connections.values():
            connection.delete()
        super(RPC_Handler, self).delete()
        
    def __getstate__(self):
        state = super(RPC_Handler, self).__getstate__()
        state["current_connections"] = {}
        return state
                  
        
class Secure_Socket(mpre.networkssl.SSL_Socket):
   
    defaults = mpre.networkssl.SSL_Socket.defaults.copy()
    defaults.update({"authentication_token" : '0'})
    
    def send(self, data):
        data = self.authentication_token + ' ' + data
        return super(Secure_Socket, self).send(data)
    
    def recv(self, buffer_size=0):
        return super(Secure_Socket, self).recv(buffer_size).split(' ', 1)
        

class Secure_Client(mpre.networkssl.SSL_Client):
            
    defaults = mpre.networkssl.SSL_Client.defaults.copy()
    defaults.update({"authentication_token" : '0'})
    
    def send(self, data):
        data = self.authentication_token + ' ' + data    
        return super(Secure_Client, self).send(data)
        
    def recv(self, buffer_size=0):
        return super(Secure_Client, self).recv(buffer_size).split(' ', 1) 
        
        
class RPC_Server(mpre.networkssl.SSL_Server):
    
    defaults = mpre.networkssl.SSL_Server.defaults.copy()
    defaults.update({"port" : 40022,
                     "interface" : "localhost",
                     "Tcp_Socket_type" : "mpre.rpc.RPC_Request"})
                     
    
class RPC_Requester(Secure_Client):
    
    defaults = Secure_Client.defaults.copy()
    defaults.update({"dont_save" : True,
                     "authentication_client" : "mpre.rpc.Environment_Access_Client",
                     "callback" : None})
    
    def __init__(self, **kwargs):
        self._requests, self._callbacks = [], []
        super(RPC_Requester, self).__init__(**kwargs)

    def on_authentication(self):
        self.callback, request = self._requests.pop(0)
        self.send(request)
    
    def make_request(self, callback, request, high_priority=False):
        if not self.callback and self.ssl_authenticated:
            self.callback = callback
            self.send(request)
        elif high_priority:
            self._requests.insert(0, (callback, request))
        else:
            self._requests.append((callback, request))
        
    def recv(self, buffer_size=0):
        auth_token, packet = super(RPC_Requester, self).recv(buffer_size)
      #  print auth_token
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
                
 
class RPC_Request(Secure_Socket):
    
    defaults = Secure_Socket.defaults.copy()
    defaults.update({"dont_save" : True,
                     "rpc_verbosity" : 'vv'})
   
    verbosity = {"execution" : 'vv',
                 "exception" : 0}
                 
    def recv(self, buffer_size=0):
        auth_token, request = super(RPC_Request, self).recv(buffer_size)
        host_info = self.getpeername()        
        $Security_Context.set_context(auth_token, host_info)
        
        component_name, method, argument_bytestream = request.split(" ", 2)
        instance = objects[component_name]
                        
        environment_access = $Environment_Access        
                
        if (host_info[0] in ("localhost", "127.0.0.1") or 
            environment_access.validate() or
            (instance is environment_access and 
             method in ("login", "register"))):
            try:
                args, kwargs = pickle.loads(argument_bytestream)
                call = getattr(instance, method)
                self.alert("\n\nExecuting {}.{}", [component_name, method], 
                           level=self.verbosity["execution"])
                response = pickle.dumps(call(*args, **kwargs))
            except BaseException as error:
                if not isinstance(error, SystemExit):
                    self.alert("Exception when executing {}.{}\n{}", 
                               [component_name, method, error], 
                               level=self.verbosity["exception"])
                response = pickle.dumps(error, pickle.HIGHEST_PROTOCOL)      
        else:
            self.alert("Denying rpc {}.{} from host {}",
                       (instance.instance_name, method, host_info))
            response = pickle.dumps(mpre.authentication.UnauthorizedError())
        $Security_Context.set_context(None, None)
        self.send(response)
        