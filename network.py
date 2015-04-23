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
    
    def bad_target(self, sock, error):
        sock.alert("Invalid target {}; {} {}", 
                   [getattr(sock, "target", ''), errno.errorcode[error.errno], error], 
                   level='v')
        sock.delete()
        
    def unhandled(self, sock, error):
        sock.alert("Unhandled error:{} {}", [errno.errorcode[error.errno], error], level=0)
        sock.delete()
        
_error_handler = Error_Handler()
       
class Socket(base.Wrapper):
    """ Provides a mostly transparent asynchronous socket interface by applying a 
        Wrapper to a _socketobject. The default socket family is socket.AF_INET and
        the default socket type is socket.SOCK_STREAM (a.k.a. a tcp socket)."""
    defaults = defaults.Socket

    def _get_address(self):
        return (self.ip, self.port)
    address = property(_get_address)
    
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM,
                       proto=0, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(family, type, proto))
        self.error_handler = _error_handler
        super(Socket, self).__init__(**kwargs)
        self.socket = self.wrapped_object
        self.setblocking(self.blocking)
        self.settimeout(self.timeout)
                
        if self.add_on_init:
            self.added_to_network = True
            self.parallel_method("Network", "add", self)
         
    def on_select(self):
        """ Used to customize behavior when a socket is readable according to select.select.
            It is not likely that one would overload this method; End users probably want
            to overload recv/recvfrom instead."""
        self.recvfrom(self.network_packet_size)
        
    def send(self, data):
        """ Sends data via the underlying _socketobject. The socket is first checked to
            ensure writability before sending. If the socket is not writable, NotWritableError is raised. Usage of this method requires a connected socket"""
        print self.instance_name, "Sending data"
        if self.parallel_method("Network", "is_writable", self):
            return self.wrapped_object.send(data)
        else:
            raise NotWritableError
                             
    def sendto(self, data, host_info):
        """ Sends data via the underlying _socketobject to the specified address. The socket
            is first checked to ensure writability before sending. If the socket is not
            writable, NotWritableError is raised."""
        if self.parallel_method("Network", "is_writable", self):
            return self.wrapped_object.sendto(data, host_info)
        else:
            raise NotWritableError

    def recv(self, buffer_size=0):
        """ Receives data from a remote endpoint. This method is event triggered and called
            when the socket becomes readable according to select.select. Subclasses should
            extend this method to customize functionality for when data is received. This
            method is called for Tcp sockets and requires a connection."""
        buffer_size = (self.network_packet_size if not buffer_size else
                       buffer_size)
        return self.wrapped_object.recv(buffer_size)
        
    def recvfrom(self, buffer_size=0):
        """ Receives data from a host. For Udp sockets this method is event triggered
            and called when the socket becomes readable according to select.select. Subclasses
            should extend this method to customize functionality for when data is received."""
        buffer_size = (self.network_packet_size if not buffer_size else
                       buffer_size)
        return self.wrapped_object.recvfrom(buffer_size)
      
    def connect(self, address):
        """ Perform a non blocking connect to the specified address. The on_connect method
            is called when the connection succeeds, or the appropriate error handler method
            is called if the connection fails. Subclasses should overload on_connect instead
            of this method."""
        try:
            self.wrapped_object.connect(address)
        except socket.error as error:
            if error.errno != 10035:
                raise
            if not self._connecting:
                self._connecting = True
                self.parallel_method("Network", "connect", self)            

    def on_connect(self):
        """ Performs any logic required when a Tcp connection succeeds. This method should
            be overloaded by subclasses."""
        self.alert("Connected", level=0)
                
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
                    
    def on_select(self):
        try:
            while True:
                self.accept()
        except socket.error as error:
            if error.errno != 10035:
                raise
                
    def accept(self):
        _socket, address = self.wrapped_object.accept()
        
        connection = self.create(self.Tcp_Socket_type,
                                 wrapped_object=_socket)
        
        self.alert("{} accepted connection {} from {}", 
                  (self.name, connection.instance_name, address),
                  level="v")
        
        self.on_connect(connection)
        return connection, address
        
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
        """ Connection logic that the server should apply when a new client has connected.
            This method should be overloaded by subclasses"""
        raise NotImplementedError 
        
        
class Tcp_Client(Tcp_Socket):

    defaults = defaults.Tcp_Client

    def __init__(self, **kwargs):
        super(Tcp_Client, self).__init__(**kwargs)
        
        if not self.target:
            if not self.ip:
                self.alert("Attempted to create Tcp_Client with no host ip or target", tuple(), 0)
            self.target = (self.ip, self.port)
        if self.auto_connect:
            self.connect(self.target)
                
        
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
    """ Manages socket objects and is responsible for calling select.select to determine
        readability/writability of sockets. Also responsible for non blocking connect logic. 
        This component is created by default upon application startup, and in most cases will
        not require user interaction."""
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
        self._sockets = set()
        self.running = False
        self.update_instruction = Instruction(self.instance_name, "_update_range_size")
        self.update_instruction.execute(self.update_priority)
        
    def add(self, sock):
        super(Network, self).add(sock)
        self.sockets.append(sock)
        self._sockets.add(sock)
        if not self.running:
            self.running = True        
            self.run()
                
    def remove(self, sock):
        super(Network, self).remove(sock)
        self.sockets.remove(sock)
        self._sockets.remove(sock)
        if sock in self.connecting:
            self.connecting.remove(sock)
            
    def delete(self):
        super(Network, self).delete()
        del self.sockets
        del self._sockets
        
    def _update_range_size(self):
        load = self._socket_range_size = range((len(self.sockets) / 500) + 1)
        # disable sleep under load
        self.priority = self.defaults["priority"] if len(load) == 1 else 0.0 
        self.update_instruction.execute(self.update_priority)

    def run(self):
        sockets = self.sockets
        if not sockets:
            self.running = False
        else:
            for chunk in self._socket_range_size:
                # select has a max # of file descriptors it can handle, which
                # is about 500 (at least on windows). We can avoid this limitation
                # by sliding through the socket list in slices of 500 at a time
                socket_list = sockets[self._slice_mapping[chunk]]
                readable, writable, errors = select.select(socket_list, socket_list, [], 0.0)
                                
                writable = self._writable = set(writable)
                connecting = self.connecting
                #print "{}/{} are connecting".format(len(connecting), len(socket_list))
                if connecting:
                    # if a tcp client is writable, it's connected
                    accepted_connections = connecting.intersection(writable)
                    if accepted_connections:
                        for accepted in connecting.intersection(writable):
                            accepted.on_connect()
                        
                    # if not, then it's still connecting or the connection failed
                    still_connecting = connecting.difference(writable)    
                    expired = set()                    
                    if still_connecting:                        
                        for connection in still_connecting:
                            connection.connection_attempts -= 1
                            if not connection.connection_attempts:
                                try:
                                    connection.connect(connection.target)
                                except socket.error as error:
                                    handler = getattr(connection.error_handler, 
                                        ERROR_CODES[error.errno].lower(),
                                        connection.error_handler.unhandled)
                                    handler(connection, error)
                                    expired.add(connection)
                    self.connecting = still_connecting.difference(expired)          
             #   print "Total still connecting: ", len(self.connecting)
                if readable:
                    for sock in readable:
                        try:
                            sock.on_select()
                        except socket.error as error:
                            handler = getattr(sock.error_handler, 
                                    ERROR_CODES[error.errno].lower(),
                                    sock.error_handler.unhandled)
                            handler(sock, error)         
            self.run_instruction.execute(priority=self.priority)
                   
    def connect(self, sock):
        self.connecting.add(sock)
    
    def is_writable(self, sock):
        return sock in self._writable