#   mpf.network_library - Asynchronous socket operations
#
#    Copyright (C) 2014  Ella Rose
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
import socket
import select
import struct
import errno
import traceback

import mpre
import mpre.vmlibrary as vmlibrary
import mpre.defaults as defaults
import mpre.base as base
from utilities import Latency, Average
Instruction = mpre.Instruction

NotWritableError = type("NotWritableError", (IOError, ), {"errno" : -1})
ERROR_CODES = {-1 : "NotWritableError"}
try:
    CALL_WOULD_BLOCK = errno.WSAEWOULDBLOCK
    BAD_TARGET = errno.WSAEINVAL
    CONNECTION_IN_PROGRESS = errno.WSAEWOULDBLOCK
    CONNECTION_IS_CONNECTED = errno.WSAEISCONN
    CONNECTION_WAS_ABORTED = errno.WSAECONNABORTED
    CONNECTION_RESET = errno.WSAECONNRESET
    
    ERROR_CODES[BAD_TARGET] = "BAD_TARGET"
    
except:
    CALL_WOULD_BLOCK = errno.EWOULDBLOCK
    CONNECTION_IN_PROGRESS = errno.EINPROGRESS
    CONNECTION_IS_CONNECTED = errno.EISCONN
    CONNECTION_WAS_ABORTED = errno.ECONNABORTED
    CONNECTION_RESET = errno.ECONNRESET
 
ERROR_CODES.update({CALL_WOULD_BLOCK : "CALL_WOULD_BLOCK",
                    CONNECTION_IN_PROGRESS : "CONNECTION_IN_PROGRESS",
                    CONNECTION_IS_CONNECTED : "CONNECTION_IS_CONNECTED",
                    CONNECTION_WAS_ABORTED : "CONNECTION_WAS_ABORTED",
                    CONNECTION_RESET  : "CONNECTION_RESET"})
               
HOST = socket.gethostbyname(socket.gethostname())

class Error_Handler(object):
            
    def connection_reset(self, sock, error):
        sock.alert("Connection reset\n{}", [error], level=0)
        sock.delete()
        
    def connection_was_aborted(self, sock, error):
        sock.alert("Connection was aborted\n{}", [error], level=0)
        sock.delete()
        
    def eagain(self, sock, error):
        sock.alert("{}", [error], level=0)
        
    def unhandled(self, sock, error):
        sock.alert("Unhandled error:\n{}", [error], level=0)
        
        
class Socket(base.Wrapper):

    defaults = defaults.Socket

    def _get_address(self):
        return (self.ip, self.port)
    address = property(_get_address)
    
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM,
                       proto=0, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(family, type, proto))
        super(Socket, self).__init__(**kwargs)
        self.socket = self.wrapped_object
        self.setblocking(self.blocking)
        self.settimeout(self.timeout)
        self.error_handler = Error_Handler()
        
        if self.add_on_init:
            self.added_to_network = True
            self.parallel_method("Network", "add", self)
         
    def on_select(self):
        self.recvfrom(self.network_packet_size)
        
    def send(self, data):
        if self.parallel_method("Network", "is_writable", self):
            return self.wrapped_object.send(data)
        else:
            raise NotWritableError
                             
    def sendto(self, data, host_info):
        if self.parallel_method("Network", "is_writable", self):
            return self.wrapped_object.sendto(data, host_info)
        else:
            raise NotWritableError

    def recv(self, buffer_size=0):
        buffer_size = (self.network_packet_size if not buffer_size else
                       buffer_size)
        return self.wrapped_object.recv(buffer_size)
        
    def recvfrom(self, buffer_size=0):
        buffer_size = (self.network_packet_size if not buffer_size else
                       buffer_size)
        return self.wrapped_object.recvfrom(buffer_size)
      
    def connect(self, address):
        try:
            self.wrapped_object.connect(address)
        except socket.error:
            self.parallel_method("Network", "connect", self)   
        
    def on_connect(self):
        self.alert("Connected", level=0)
        #raise NotImplementedError
        
    def delete(self):
        if not self.closed:
            self.close()        
        super(Socket, self).delete()
    
    def close(self):
        if self.added_to_network:
            self.parallel_method("Network", "remove", self)
        self.wrapped_object.close()
        self.closed = True
    
    def __getstate__(self):
        stats = super(Socket, self).__getstate__()
        del stats["wrapped_object"]
        del stats["socket"]
        return stats
        
       
class Tcp_Socket(Socket):

    defaults = defaults.Tcp_Socket
    
    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET,
                                                          socket.SOCK_STREAM))
        super(Tcp_Socket, self).__init__(**kwargs)

    def on_select(self):
        self.recv(self.network_packet_size)
        
        
class Server(Tcp_Socket):

    defaults = defaults.Server

    def __init__(self, **kwargs):       
        super(Server, self).__init__(**kwargs)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, self.reuse_port)

        bind_success = True
        try:
            self.bind((self.interface, self.port))
        except socket.error:
            self.alert("socket.error when binding to {0}", (self.port, ), 0)
            bind_success = self.handle_bind_error()
        if bind_success:
            self.listen(self.backlog)

    def recv(self):
        _socket, address = self.accept()
        
        connection = self.create(self.Tcp_Socket_type,
                                 wrapped_object=_socket)
        
        self.alert("{} accepted connection {} from {}", 
                  (self.name, connection.instance_name, address),
                  level="v")
        
        self.on_connect(connection)

    def handle_bind_error(self):
        if self.allow_port_zero:
            self.bind((self.interface, 0))
            return True
        else:
            self.alert("{0}\nAddress already in use. Deleting {1}\n",
                       (traceback.format_exc(), self.instance_name), 0)
            instruction = Instruction(self.instance_name, "delete")
            instruction.execute()
 
    def on_connect(self, connection):
        raise NotImplementedError 
        
        
class Tcp_Client(Tcp_Socket):

    defaults = defaults.Tcp_Client

    def __init__(self, **kwargs):
        super(Tcp_Client, self).__init__(**kwargs)
        
        if not self.target:
            if not self.ip:
                self.alert("Attempted to create Tcp_Client with no host ip or target", tuple(), 0)
            self.target = (self.ip, self.port)
                        
        
class Udp_Socket(Socket):

    defaults = defaults.Udp_Socket

    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        super(Udp_Socket, self).__init__(**kwargs)        
               
        if self.bind_on_init:
            self.bind((self.interface, self.port))
            
        if not self.port:
            self.port = self.getsockname()[1]
                   
        
class Multicast_Beacon(Udp_Socket):

    defaults = defaults.Multicast_Beacon

    def __init__(self, **kwargs):
        super(Multicast_Beacon, self).__init__(**kwargs)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.packet_ttl)


class Multicast_Receiver(Udp_Socket):

    defaults = defaults.Multicast_Receiver

    def __init__(self, **kwargs):
        super(Multicast_Receiver, self).__init__(**kwargs)

        # thanks to http://pymotw.com/2/socket/multicast.html for the below
        group_option = socket.inet_aton(self.address)
        multicast_configuration = struct.pack("4sL", group_option, socket.INADDR_ANY)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_configuration)
           

class Network(vmlibrary.Process):

    defaults = defaults.Network
   
    def __init__(self, **kwargs):
        # minor optimization; pre allocated slices and ranges for
        # sliding through the socket list to sidestep the 500 
        # file descriptor limit that select has. Produces slice objects
        # for ranges 0-500, 500-1000, 1000-1500, etc, up to 50000.
        self._slice_mapping = dict((x, slice(x * 500, (500 + x * 500))) for 
                                    x in xrange(100))
        self._socket_range_size = range(1)
        
        self._writable = set()
        self.connecting = set()
        super(Network, self).__init__(**kwargs)
        
        self.sockets = []
        self.running = False
        self.update_instruction = Instruction("Network", "_update_range_size")        
          
    def add(self, sock):
        super(Network, self).add(sock)
        self.sockets.append(sock)
        if not self.running:
            self.run_instruction.execute(priority=self.priority)
            self.running = True        
    
    def remove(self, sock):
        super(Network, self).remove(sock)
        self.sockets.remove(sock)
                
    def delete(self):
        super(Network, self).delete()
        del self.sockets
        
    def _update_range_size(self):
        self._socket_range_size = range((len(self.sockets) / 500) + 1)
        self.update_instruction.execute(self.update_priority)

    def run(self):
        sockets = self.sockets
        if sockets:
            for chunk in self._socket_range_size:
                # select has a max # of file descriptors it can handle, which
                # is about 500 (at least on windows). We can avoid this limitation
                # by sliding through the socket list in slices of 500 at a time
                socket_list = sockets[self._slice_mapping[chunk]]
                readable, writable, errors = select.select(socket_list, socket_list, [], 0.0)
                
                writable = self._writable = set(writable)
                connecting = self.connecting
                if connecting:
                    for accepted in connecting.intersection(writable):
                        accepted.on_connect()
                    
                    self.connecting = still_connecting = connecting.difference(writable)
                    for connection in still_connecting:
                        connection.connection_attempts -= 1
                        if not connection.connection_attempts:
                            try:
                                connection.connect(connection.address)
                            except socket.error:
                                handler = getattr(sock.error_handler, 
                                    ERROR_CODES[error.errno].lower(),
                                    sock.error_handler.unhandled)
                                handler(sock, error)                               
                                    
                for sock in readable:
                    try:
                        sock.on_select()
                    except socket.error as error:
                        handler = getattr(sock.error_handler, 
                                  ERROR_CODES[error.errno].lower(),
                                  sock.error_handler.unhandled)
                        handler(sock, error)         

            self.run_instruction.execute(priority=self.priority)
        else:
            self.running = False
                   
    def connect(self, sock):
        self.connecting.add(sock)
        
    def is_writable(self, sock):
        return sock not in self.connecting and sock in self._writable