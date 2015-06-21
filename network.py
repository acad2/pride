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
import sys
import binascii

import mpre
import mpre.vmlibrary as vmlibrary
import mpre.base as base
from utilities import Latency, Average
Instruction = mpre.Instruction
objects = mpre.objects

NotWritableError = type("NotWritableError", (IOError, ), {"errno" : -1})
ERROR_CODES = {-1 : "NotWritableError"}
try:
    CALL_WOULD_BLOCK = errno.WSAEWOULDBLOCK
    BAD_TARGET = errno.WSAEINVAL
    CONNECTION_IN_PROGRESS = errno.WSAEWOULDBLOCK
    CONNECTION_IS_CONNECTED = errno.WSAEISCONN
    CONNECTION_WAS_ABORTED = errno.WSAECONNABORTED
    CONNECTION_RESET = errno.WSAECONNRESET
    CONNECTION_CLOSED = errno.WSAEDISCON
    ERROR_CODES[BAD_TARGET] = "BAD_TARGET"    
except:
    CALL_WOULD_BLOCK = errno.EWOULDBLOCK
    CONNECTION_IN_PROGRESS = errno.EINPROGRESS
    CONNECTION_IS_CONNECTED = errno.EISCONN
    CONNECTION_WAS_ABORTED = errno.ECONNABORTED
    CONNECTION_RESET = errno.ECONNRESET
    CONNECTION_CLOSED = errno.ENOTCONN
 
ERROR_CODES.update({CALL_WOULD_BLOCK : "CALL_WOULD_BLOCK",
                    CONNECTION_IN_PROGRESS : "CONNECTION_IN_PROGRESS",
                    CONNECTION_IS_CONNECTED : "CONNECTION_IS_CONNECTED",
                    CONNECTION_WAS_ABORTED : "CONNECTION_WAS_ABORTED",
                    CONNECTION_RESET  : "CONNECTION_RESET",
                    CONNECTION_CLOSED : "CONNECTION_CLOSED"})
               
HOST = socket.gethostbyname(socket.gethostname())

class Error_Handler(object):
    
    def connection_closed(self, sock, error):
        sock.alert("{}", [error], level=0)
        sock.delete()
        
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
                   level=0)
        sock.delete()
        
    def unhandled(self, sock, error):
        sock.alert("Unhandled error:{} {}", [errno.errorcode[error.errno], error], level=0)
        sock.delete()
        
_error_handler = Error_Handler()
       
class Socket(base.Wrapper):
    """ Provides a mostly transparent asynchronous socket interface by applying a 
        Wrapper to a _socketobject. The default socket family is socket.AF_INET and
        the default socket type is socket.SOCK_STREAM (a tcp socket)."""
    defaults = base.Wrapper.defaults.copy()
    additional_defaults = {"blocking" : 0,
                           "timeout" : 0,
                           "add_on_init" : True,
                           "recvfrom_packet_size" : 65535,
                           "recv_packet_size" : 32768,
                           "socket_family" : socket.AF_INET,
                           "socket_type" : socket.SOCK_STREAM,
                           "protocol" : socket.IPPROTO_IP,
                           "interface" : "0.0.0.0",
                           "port" : 0,
                           "connection_attempts" : 10,
                           "bind_on_init" : False,
                           "closed" : False,
                           "_connecting" : False,
                           "added_to_network" : False,
                           "replace_reference_on_load" : False}
    defaults.update(additional_defaults)
    
    additional_parser_ignores = additional_defaults.keys()
    additional_parser_ignores.remove("interface")
    additional_parser_ignores.remove("port")
    parser_ignore = base.Wrapper.parser_ignore + tuple(additional_parser_ignores)
    
    _buffer = bytearray(1024 * 1024)
    _memoryview = memoryview(_buffer)
    
    def _get_address(self):
        return (self.ip, self.port)
    address = property(_get_address)
    
    def _get_os_recv_buffer_size(self):
        return self.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        
    def _set_os_recv_buffer_size(self, size):
        self.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, size)
    os_recv_buffer_size = property(_get_os_recv_buffer_size, _set_os_recv_buffer_size)  
    
    def _get_os_send_buffer_size(self):
        return self.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
        
    def _set_os_send_buffer_size(self, size):
        self.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, size)
    os_send_buffer_size = property(_get_os_send_buffer_size, _set_os_send_buffer_size)
    
    wrapped_object_name = 'socket'
    
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM,
                       proto=0, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(family, type, proto))
        self.error_handler = _error_handler
        super(Socket, self).__init__(**kwargs)
        self.setblocking(self.blocking)
        self.settimeout(self.timeout)
        
        if self.add_on_init:
            self.added_to_network = True
            try:
                objects["Network"].add(self)
            except KeyError:
                self.alert("Network component does not exist", level=0)
         
    def on_select(self):
        """ Used to customize behavior when a socket is readable according to select.select.
            It is not likely that one would overload this method; End users probably want
            to overload recv/recvfrom instead."""
        return self.recvfrom()
 
    def recv(self, buffer_size=0):
        """ Receives data from a remote endpoint. This method is event triggered and called
            when the socket becomes readable according to select.select. This
            method is called for Tcp sockets and requires a connection.
            
            Note that this recv will return the entire contents of the OS buffer and 
            does not need to be called in a loop."""
        buffer_size = buffer_size or self.recv_packet_size 
        _memoryview = self._memoryview
        _byte_count = 0        
        try:
            while True:
                byte_count = self.socket.recv_into(_memoryview[_byte_count:], buffer_size)
                if not byte_count:
                    break
                _byte_count += byte_count                
        except socket.error as error:
            if error.errno != 10035:
                raise        
        return bytes(self._buffer[:_byte_count])
        
    def recvfrom(self, buffer_size=0):
        """ Receives data from a host. For Udp sockets this method is event triggered
            and called when the socket becomes readable according to select.select. Subclasses
            should extend this method to customize functionality for when data is received."""
        byte_count, _from = self.socket.recvfrom_into(self._memoryview, 
                                                      buffer_size or self.recvfrom_packet_size)
        return bytes(self._buffer[:byte_count]), _from
    
    #def send(self, data):
    #    byte_count = len(data)
    #    difference = self.socket.send(data) - byte_count
    #    if difference:
            
        
    def connect(self, address):
        """ Perform a non blocking connect to the specified address. The on_connect method
            is called when the connection succeeds, or the appropriate error handler method
            is called if the connection fails. Subclasses should overload on_connect instead
            of this method."""
        if address[0] == "0.0.0.0":
            address = ("localhost", address[1])
        self.target = address
        try:
            self.wrapped_object.connect(address)
        except socket.error as error:
            if not self._connecting:
                self._connecting = True
                objects["Network"].connecting.add(self)
            else:
                raise
        else:
            self.on_connect()
            
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
            objects["Network"].remove(self)
        self.wrapped_object.close()
        self.closed = True
    
    def __getstate__(self):
        stats = super(Socket, self).__getstate__()
        del stats["wrapped_object"]
        del stats["socket"]
        return stats
        
 
class Raw_Socket(Socket):
    
    defaults = Socket.defaults.copy()
    defaults.update({"socket_type" : socket.SOCK_RAW,
                     "protocol" : 0})
    
    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET, 
                                                          socket.SOCK_RAW, 
                                                          Raw_Socket.defaults["protocol"]))
        super(Raw_Socket, self).__init__(**kwargs)
        
        
class Packet_Sniffer(Raw_Socket):
            
    defaults = Raw_Socket.defaults.copy()
    defaults.update({"IP_HDRINCL" : 1})
    
    parser_ignore = Raw_Socket.parser_ignore + ("IP_HDRINCL", )
    
    def __init__(self, **kwargs):
        super(Packet_Sniffer, self).__init__(**kwargs)
        self.bind((self.interface, self.port))
        self.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, self.IP_HDRINCL)
        if "nt" in sys.platform:
            self.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
            
    def close(self):
        self.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        super(Packet_Sniffer, self).close()
        
    #def recvfrom(self):
    #    packet, _from = super(Packet_Sniffer, self).recvfrom()
    #    print len(packet), packet
    #    ethernet_header = struct.unpack("!6s6s2s", packet[:14])
    #    print "Ethernet: destination mac: ", binascii.hexlify(ethernet_header[0])
    #    print "Ethernet: source mac: ", binascii.hexlify(ethernet_header[1])
    #    print "Ethernet: type: ", binascii.hexlify(ethernet_header[2])
    #    
    #    ip_header, source_ip, destination_ip = struct.unpack("!12s4s4s", packet[14:34])
    #    print "Ip header: ", str(binascii.hexlify(ip_header))
    #    print "Source address: ", str(binascii.hexlify(source_ip))
    #    print "Destination address: ", str(binascii.hexlify(destination_ip))
    #    if ord(ip_header[10]) == 6: # tcp header
    #        tcp_header = struct.unpack("!2s2s16s", packet[34:54])
    #        print "Tcp header: ", tcp_header
    #    elif ord(ip_header[10]) == 17:
    #        udp_header = struct.unpack("!HH", packet[34:42])
    #        print "udp header: ", udp_header
        
        
class Tcp_Socket(Socket):

    defaults = Socket.defaults.copy()
    defaults.update({"socket_family" : socket.AF_INET,
                     "socket_type" : socket.SOCK_STREAM,
                     "dont_save" : True})
    
    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET,
                                                          socket.SOCK_STREAM))
        super(Tcp_Socket, self).__init__(**kwargs)

    def on_select(self):
        self.recv()
        
        
class Server(Tcp_Socket):

    defaults = Tcp_Socket.defaults.copy()
    defaults.update({"port" : 80,
                     "backlog" : 50,
                     "reuse_port" : 0,
                     "Tcp_Socket_type" : "network.Tcp_Socket"})

    parser_ignore = Tcp_Socket.parser_ignore + ("backlog", "reuse_port", "Tcp_Socket_type")
    
    def __init__(self, **kwargs):       
        super(Server, self).__init__(**kwargs)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, self.reuse_port)

        bind_success = True
        try:
            self.bind((self.interface, self.port))
        except socket.error:
            self.alert("socket.error when binding to {}", (self.port, ), 0)
            bind_success = self.handle_bind_error()
        if bind_success:
            self.alert("Listening at: {}:{}".format(self.interface, self.port), level='v')
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
                                 
        self.on_connect(connection, address)
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
 
    def on_connect(self, connection, address):
        """ Connection logic that the server should apply when a new client has connected.
            This method should be overloaded by subclasses"""
        self.alert("accepted connection {} from {}", 
                  (connection.instance_name, address),level="v")
        
        
class Tcp_Client(Tcp_Socket):

    defaults = Tcp_Socket.defaults.copy()
    defaults.update({"ip" : "",
                     "port" : 80,
                     "target" : tuple(),
                     "auto_connect" : True,
                     "as_port" : 0})
    
    parser_ignore = Tcp_Socket.parser_ignore + ("target", "auto_connect", "as_port")
    
    def __init__(self, **kwargs):
        super(Tcp_Client, self).__init__(**kwargs)        
        if self.as_port:
            self.bind((self.interface, self.as_port))
            
        if not self.target:
            if not self.ip:
                self.alert("Attempted to create Tcp_Client with no host ip or target", tuple(), 0)
            self.target = (self.ip, self.port)
        if self.auto_connect:
            self.connect(self.target)
                
        
class Udp_Socket(Socket):

    defaults = Socket.defaults.copy()
    defaults.update({"bind_on_init" : True})
    del defaults["connection_attempts"]

    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        super(Udp_Socket, self).__init__(**kwargs)        
               
        if self.bind_on_init:
            self.bind((self.interface, self.port))
            
        if not self.port:
            self.port = self.getsockname()[1]
        
        
class Multicast_Beacon(Udp_Socket):

    defaults = Udp_Socket.defaults.copy()
    defaults.update({"packet_ttl" : struct.pack("b", 127),
                     "multicast_group" : "224.0.0.0",
                     "multicast_port" : 1929})

    parser_ignore = Udp_Socket.parser_ignore + ("packet_ttl", )
    
    def __init__(self, **kwargs):
        super(Multicast_Beacon, self).__init__(**kwargs)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.packet_ttl)


class Multicast_Receiver(Udp_Socket):

    defaults = Udp_Socket.defaults.copy()
    defaults.update({"address" : "224.0.0.0"})

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
    defaults = vmlibrary.Process.defaults.copy()
    defaults.update({"number_of_sockets" : 0,
                     "priority" : .01,
                     "update_priority" : 5,
                     "_updating" : False,
                     "auto_start" : False})
   
    def __init__(self, **kwargs):
        # minor optimization; pre allocated slices and ranges for
        # sliding through the socket list to sidestep the 500 
        # file descriptor limit that select has. Produces slice objects
        # for ranges 0-500, 500-1000, 1000-1500, etc, up to 50000.
        self._slice_mapping = dict((x, slice(x * 500, (500 + x * 500))) for 
                                    x in xrange(100))
        self._socket_range_size = range(1)
        
        self.writable = set()
        self.connecting = set()
        super(Network, self).__init__(**kwargs)
        
        self.sockets = []
        self._sockets = set()
        self.running = False
        self.update_instruction = Instruction(self.instance_name, "_update_range_size")
        #self.update_instruction.execute(self.update_priority)
        
    def add(self, sock):
        super(Network, self).add(sock)
        self.sockets.append(sock)
        self._sockets.add(sock)
        if not self.running:
            self.running = True        
            self._run()
                
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
            connecting = self.connecting
            self.connecting = _connecting = set()
            writable = self.writable = set()
            expired = set()
            still_connecting = set()      
            for chunk in self._socket_range_size:
                # select has a max # of file descriptors it can handle, which
                # is about 500 (at least on windows). We can avoid this limitation
                # by sliding through the socket list in slices of 500 at a time
                socket_list = sockets[self._slice_mapping[chunk]]
                readable, _writable, errors = select.select(socket_list, socket_list, [], 0.0)
                                
                writable.update(_writable)              
                # if a tcp client is writable, it's connected     
                for accepted in connecting.intersection(writable):
                    accepted.on_connect()
                    
                # if not, then it's still waiting or the connection timed out
                still_connecting = connecting.difference(writable)
                for connection in still_connecting:
                    connection.connection_attempts -= 1
                    #connection.alert("Attempts remaining: {}".format(connection.connection_attempts), level=0)
                    if not connection.connection_attempts:
                        try:
                            connection.connect(connection.target)
                        except socket.error as error:
                            expired.add(connection)
                            handler = getattr(connection.error_handler, 
                                ERROR_CODES[error.errno].lower(),
                                connection.error_handler.unhandled)
                            handler(connection, error)                                   
                _connecting.update(still_connecting.difference(expired))
                
                if readable:
                    for sock in readable:
                        try:
                            sock.on_select()
                        except socket.error as error:
                            handler = getattr(sock.error_handler, 
                                    ERROR_CODES[error.errno].lower(),
                                    sock.error_handler.unhandled)
                            handler(sock, error)         