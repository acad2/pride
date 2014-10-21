import socket
import select
import struct
import errno
import time
import mmap

import defaults
import base
Event = base.Event

try:
    CONNECTION_IN_PROGRESS = errno.WSAEWOULDBLOCK
    CONNECTION_IS_CONNECTED = errno.WSAEISCONN
    CONNECTION_WAS_ABORTED = errno.WSAECONNABORTED
except:
    CONNECTION_IN_PROGRESS = errno.EINPROGRESS
    CONNECTION_IS_CONNECTED = errno.EISCONN
    CONNECTION_WAS_ABORTED = errno.ECONNABORTED
    
    
class Connection(base.Wrapper):
    
    defaults = defaults.Connection
    def _get_protocol(self):
        return (self.on_connection, self.incoming, self.outgoing)
        
    def _set_protocol(self, protocol):
        on_connection, incoming, outgoing = protocol
        self.on_connection = on_connection
        self.incoming = incoming
        self.outgoing = outgoing
    protocol = property(_get_protocol, _set_protocol)        

    on_connection = None
    incoming = None
    outgoing = None
    def __init__(self, sock=None, *args, **kwargs):     
        if not sock:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        super(Connection, self).__init__(sock, *args, **kwargs)
        sock.setblocking(0)
         
            
class Server(Connection):
    """usage: Event("Network_Manager0", "create", "networklibrary.Server",
    incoming=myincoming, outgoing=myoutgoing, on_connection=myonconnection,
    name="My_Server", port=40010).post()"""
    
    defaults = defaults.Server
    
    def __init__(self, *args, **kwargs):
        self.inbound_connection_options = {}
        super(Server, self).__init__(*args, **kwargs)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, self.reuse_port)
        self.bind((self.host_name, self.port))
        self.listen(self.backlog)        
        self.parent.servers.append(self)
        Event("Service_Listing0", "add_local_service", (self.host_name, self.port), self.name).post()
        
        
class Outbound_Connection(Connection):
    
    defaults = defaults.Outbound_Connection
    
    def __init__(self, *args, **kwargs):
        super(Outbound_Connection, self).__init__(*args, **kwargs)      
        Event("Network_Manager0", "buffer_connection", self, self.target).post()
       

class Download(Outbound_Connection):
    
    defaults = defaults.Download
    
    def __init__(self, *args, **kwargs):
        super(Download, self).__init__(*args, **kwargs)
        if not self.filename:
            self.warning("Attempted to start a download without a filename to use")
            self.delete()
        self.file = open("%s_filename" % self.filename_prefix, "wb")      
        
    def on_connection(self, connection, address):
        request = ":".join((self.filename, "0", str(self.network_chunk_size)))
        print "sending download request: ", request
        Event("Network_Manager0", "buffer_data", connection, request).post()
        
    def outgoing(self, connection, data):
        connection.send(data)
        
    def incoming(self, connection):
        response = connection.recv(self.network_chunk_size)
        if response:
            if self.download_in_progress:
                position, data = response.split(self.delimiter)
                end = len(data)
                print "Download received %s bytes of %s" % (end, self.filename)
                self.filesize += end
                self.file.seek(int(position))
                self.file.write(data)
                self.file.flush()
                request = ":".join((self.filename, str(end), str(end + self.network_chunk_size)))
                Event("Network_Manager0", "buffer_data", connection, request).post()
            else: # response to the request from on_connection containing file size
                self.file_size = int(response)
                print "Download started. File size: %s" % self.file_size
                self.download_in_progress = True
        else:
            print "Download complete!"
            connection.close()
            self.file.close()
            
            
class Inbound_Connection(Connection):
    
    defaults = defaults.Inbound_Connection
    
    def __init__(self, sock, *args, **kwargs):
        super(Inbound_Connection, self).__init__(sock, *args, **kwargs)
        
 
class Upload(Inbound_Connection):
    
    defaults = defaults.Upload
    
    def __init__(self, *args, **kwargs):
        super(Upload, self).__init__(*args, **kwargs)
             
    def outgoing(self, connection, data):
        connection.send(data)
        
    def incoming(self, connection): 
        try:
            filename, start, end = connection.recv(self.network_chunk_size).split(":")
        except ValueError:
            self.resource.close()
            self.delete()
        print "servicing request for %s: %s-%s" % (filename, start, end)
        if not self.resource:
            self.load_file(filename)
            Event("Network_Manager0", "buffer_data", connection, str(self.file_size)).post()
        start_int = int(start)
        end_int = int(end)
        self.resource.seek(start_int)
        data = self.resource.read(end_int - start_int)
        print "sent %s bytes of data" % len(data)
        message = "dEL!M17&R".join((start, data))
        Event("Network_Manager0", "buffer_data", connection, message).post() 
        
    def load_file(self, filename):
        _resource = resource = open(filename, "rb")
        if self.use_mmap:
            resource = mmap.mmap(_resource.fileno(), len(_resource.read()))
            _resource.close()       
        print "loaded resource: %s" % resource
        self.file_size = len(resource.read())
        self.resource = resource          
        
        
class UDP_Socket(base.Wrapper):
            
    defaults = defaults.UDP_Socket
    
    def __init__(self, *args, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        super(UDP_Socket, self).__init__(sock, *args, **kwargs)
        self.bind((self.host_name, self.port))
        self.settimeout(self.timeout)
        
        
class Multicast_Beacon(base.Wrapper):
    
    defaults = defaults.Multicast_Beacon
    
    def __init__(self, *args, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        super(Multicast_Beacon, self).__init__(sock, *args, **kwargs)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.packet_ttl)

        
class Multicast_Receiver(base.Wrapper):
    
    defaults = defaults.Multicast_Receiver
    
    def __init__(self, *args, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        super(Multicast_Receiver, self).__init__(sock, *args, **kwargs)
        #if self.reuseaddr:
        #    self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((self.listener_address, self.port))
        group_option = socket.inet_aton(self.multicast_group)
        multicast_configuration = struct.pack("4sL", group_option, socket.INADDR_ANY)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_configuration)
        # thanks to http://pymotw.com/2/socket/multicast.html for the above!
        
        
class Connection_File_Object(base.Base):
    
    def __init__(self, connection, *args, **kwargs):
        super(Connection_File_Object, self).__init__(*args, **kwargs)
        self.connection = connection
        
    def write(self, data):        
        Event("Network_Manager0", "buffer_data", self.connection, data).post()
 
 
class Basic_Authentication_Client(base.Thread):
    
    defaults = defaults.Basic_Authentication_Client
    
    def __init__(self, *args, **kwargs):
        super(Basic_Authentication_Client, self).__init__(*args, **kwargs)
        self.thread = self._new_thread()
        
    def run(self):
        next(self.thread)
        
    def _new_thread(self):
        if self.parent.auto_login:
            username = self.parent.username
            password = self.parent.password
            print "automatically logging in as %s..." % username
        else:
            print "Please provide login information for", self
            username = raw_input("Username: ")
            password = hash(raw_input("Password: "))
        response = username+"\n"+str(password)
        Event("Network_Manager0", "buffer_data", self.parent.connection, response).post()
        yield
        
        while not self.parent.network_buffer:
            yield        
        if self.parent.network_buffer in ("Invalid password", "Invalid username"):
            self.warning("%s supplied in login attempt" % self.network_buffer, "Shell")        
            self.login_stage = None
            self.network_buffer = None
            if "y" in raw_input("Retry?: ").lower():
                target = self.connection.getpeername()
                raise NotImplementedError
                Event("Network_Manager0", "create", "networklibrary.Outbound_Connection",\
                target, incoming=self.incoming, outgoing=self.outgoing,\
                on_connection=self.on_connection).post()                
                #Event("Network_Manager0", "disconnect", self.connection).post()
            else:
                self.warning("failed to login. Exiting...", self)
                Event("System0", "delete", self).post()
                raise NotImplementedError

                
class Basic_Authentication(base.Thread):
                    
    defaults = defaults.Basic_Authentication
    
    def __init__(self, connection, address, *args, **kwargs):
        super(Basic_Authentication, self).__init__(*args, **kwargs)
        self.thread = self._new_thread()
        self.connection = connection
        self.address = address
        
    def run(self):
        try:
            next(self.thread)
        except BaseException as exception:
            if type(exception) == AssertionError:
                response = "Invalid password"
            elif type(exception) == KeyError:
                response = "Invalid username"                
            elif isinstance(exception, StopIteration):
                raise                
            else:
                print "other exception occurred"
                raise
            
            Event("Network_Manager0", "buffer_data", self.connection, response).post()        
                    
    def _new_thread(self):
        while not self.parent.network_buffer[self.connection]:
            yield 
        username, password = [info for info in
                             self.parent.network_buffer[self.connection].strip().split("\n")]
        assert self.parent.authenticate[username] == hash(password)   
        self.parent.login_stage[self.address] = (username, "online")
            
                    
class Network_Manager(base.Process):

    defaults = defaults.Network_Manager
        
    def __init__(self, *args, **kwargs):
        super(Network_Manager, self).__init__(*args, **kwargs)
        self.servers = []
        self.write_buffer = {}
        self.connection_buffer = {}
        self.objects[socket.socket.__name__] = []
        self.readable_sockets = []
        self.writable_sockets = []
        Event("System0", "create", "networklibrary.Service_Listing", auto_start=False).post()
        
    def buffer_data(self, connection, data, to=None):
        if to:
            data = (to, data)
        try:
            self.write_buffer[connection].append(data)
        except KeyError:
            self.write_buffer[connection] = [data]
            
    def debuffer_data(self, connection):
        try:
            del self.write_buffer[connection]
        except KeyError:
            pass
        
    def buffer_connection(self, connection, target):
        self.connection_buffer[connection] = target
    
    def disconnect(self, connection):
        if self.write_buffer.has_key(connection):
            Event("Network_Manager0", "disconnect", connection).post()
        else:
            connection.close()
            Event("Network_Manager0", "delete", connection).post()
        
    def delete_server(self, server_name):
        for server in self.servers:
            if server.name == server_name:
                self.servers.remove(server)
                server.delete()
                
    def run(self):
        if self.connection_buffer.keys():
            #Event("Network_Manager0", "handle_connections").post()          
            self.handle_connections()
        
        if self.objects[socket.socket.__name__]:
            number_of_socket_chunks = (len(self.objects[socket.socket.__name__])/500)
            for chunk in xrange(number_of_socket_chunks+1):
                socket_list = self.objects[socket.socket.__name__][chunk*500:(1+chunk)*500]
                self.readable_sockets, self.writable_sockets, errors = select.select(\
                socket_list, socket_list, [], 0.0)    
 
                if self.readable_sockets:
                    self.handle_reads()
                    #Event("Network_Manager0", "handle_reads").post()
                if self.writable_sockets:
                    self.handle_writes()
                    #Event("Network_Manager0", "handle_writes").post()            
                
        if self in self.parent.objects[self.__class__.__name__]:
            Event("Network_Manager0", "run").post()
                
    def handle_connections(self):
        sockets = self.objects[socket.socket.__name__]
        for sock in self.connection_buffer.keys():            
            if sock in sockets:
                sockets.remove(sock)
            sock.timeout -= 1
            if not sock.timeout:
                del self.connection_buffer[sock]
                sockets.append(sock)
                Event("Network_Manager0", "delete", sock).post()
                sock.warning("Outbound Connection to %s timed out after %s frames" % (sock.target, sock.timeout))
                continue
            try: # this is how to properly do a non blocking connect
                sock.connect(self.connection_buffer[sock])
            except socket.error as error:
                if error.errno == CONNECTION_IN_PROGRESS: # waiting
                    continue
                elif error.errno == CONNECTION_IS_CONNECTED: # complete
                    self.add(sock)
                    if sock.on_connection:
                        sock.on_connection(sock, sock.getpeername())
                    del self.connection_buffer[sock]       
                        
    def handle_reads(self):
        for sock in self.readable_sockets:
            if sock in self.servers:
                connection, address = sock.accept() # inbound connection received  
                options = sock.inbound_connection_options
                _connection = self.create(sock.inbound_connection_type, connection, **options)
                for method in ("on_connection", "incoming", "outgoing"):
                    if not getattr(_connection, method):
                        setattr(_connection, method, getattr(sock, method))
                
                if sock.on_connection: # server method to apply upon connection
                    sock.on_connection(_connection, address)
                
            else: # any encoding, and the actual sock.recv is done via sock.incoming
                try:
                    sock.incoming(sock)
                except socket.error as error:
                    if error.errno == CONNECTION_WAS_ABORTED:
                        sock.close()
                        sock.delete()
                    elif error.errno == 11: # EAGAIN on unix
                        self.warning("EAGAIN error reading %s" % sock)
                        
    def handle_writes(self):
        for sock in self.writable_sockets:
            messages = self.write_buffer.get(sock)
            if messages:
                for index, message in enumerate(messages):
                    try:
                        sock.outgoing(sock, message)
                    except socket.error as error:
                        if error.errno == CONNECTION_WAS_ABORTED:
                            self.warning("Failed to send %s on %s" % (self.write_buffer[sock], sock), "%s" % error)
                            sock.delete()
                        elif error.errno == 11: # EAGAIN on unix
                            self.warning("EAGAIN error when writing to %s" % sock)
                    else:
                        del self.write_buffer[sock][index]
        
   
class Service_Listing(base.Process):
    
    defaults = defaults.Service_Listing
    
    def __init__(self, *args, **kwargs):
        super(Service_Listing, self).__init__(*args, **kwargs)
        self.local_services = {}
        self.services = {}
        
    def add_local_service(self, address, service_name):
        self.local_services[address] = service_name
        self.add_service(address)
        
    def add_service(self, address):
        host_name, port = address
        try:
            service = socket.getservbyport(port)
        except socket.error:
            try:
                service = "Local Service " + self.local_services[address]
            except KeyError:
                service = "unknown"
        self.services[address] = service
        
    def remove_local_service(self, address):
        del self.local_services[address]
        
    def remove_service(self, address):
        del self.services[address]
        
    def run(self):
        print "List of known network services: "
        for address, service_name in self.services.items():
            print "Address: %s\tService Name: %s" % (address, service_name)
        