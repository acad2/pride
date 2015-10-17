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

import pride
import pride.vmlibrary as vmlibrary
import pride.base as base
from utilities import Latency, Average
Instruction = pride.Instruction
objects = pride.objects

_socket_names, _local_connections, ERROR_CODES = {}, {}, {}

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

def local_sends(socket_send):
    def _send(self, data):
        sockname = self.sockname
        peername = self.peername
        if sockname in _local_connections: # client socket
            instance_name = _local_connections[sockname]
        elif peername[0] in ("localhost", "127.0.0.1"): # server side socket
            instance_name = _socket_names[peername]
        else:
            self.alert("Sending data over nic")        
            return socket_send(self, data)
           
        self.alert("Sending data locally, bypassing nic")
        instance = pride.objects[instance_name]
        instance._local_data += data
        instance.alert("recv called locally")
        instance.recv()            
    return _send
    
def local_recvs(socket_recv):
    def _recv(self, buffer_size=0):
        instance_name = self.instance_name
        if self._local_data:
            data = self._local_data
            self._local_data = bytes()
        else:
            data = socket_recv(self, buffer_size)
        return data
    return _recv
     
#def local_     
class Socket_Error_Handler(pride.base.Base):
    
    verbosity = {"call_would_block" : 'vv',
                 "connection_in_progress" : 0,
                 "connection_closed" : 0,
                 "connection_reset" : 0,
                 "connection_was_aborted" : 0,
                 "eagain" : 0,
                 "bad_target" : 0,
                 "unhandled" : 0,
                 "bind_error" : 0}
                 
    def dispatch(self, sock, error, error_name):
        sock.alert("{}".format(error), level=self.verbosity[error_name])
        sock.delete()
        
    def call_would_block(self, sock, error):
        if getattr(sock, "_connecting", False):
            sock.latency.finish_measuring()
            message = "Connection timed out after {:5f}\n{}"
        else:
            message = "{}"
        sock.alert(message, [error], level=self.verbosity["call_would_block"])
        sock.delete()
        
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
    
    def bind_error(self, sock, error):
        sock.alert("socket.error when binding to {}", (sock.port, ), 0)
        return sock.handle_bind_error()
        
       
class Socket(base.Wrapper):
    """ Provides a mostly transparent asynchronous socket interface by applying a 
        Wrapper to a _socketobject. The default socket family is socket.AF_INET and
        the default socket type is socket.SOCK_STREAM (a tcp socket)."""
    defaults = {"blocking" : 0,
                "timeout" : 0,
                "add_on_init" : True,                                 
                "socket_family" : socket.AF_INET,
                "socket_type" : socket.SOCK_STREAM,
                "protocol" : socket.IPPROTO_IP,
                "interface" : "0.0.0.0",
                "port" : 0,
                "_byte_count" : 0,
                "connection_attempts" : 10,
                "bind_on_init" : False,
                "closed" : False,
                "_connecting" : False,
                "_endpoint_instance_name" : '',
                "connected" : False,
                "added_to_network" : False,
                "replace_reference_on_load" : False,
                "bypass_network_stack" : True}
        
    additional_parser_ignores = defaults.keys()
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
    # note that linux is supposed to have tcp auto tuning and setting the above manually
    # may actually degrade performance. Note that on linux it is still advisable to raise
    # the system max size for buffers, which the send/recv buffers are limited to.
    # see networkutilities to modify the os buffer size.
    # windows is basically the inverse: unless explicitly set by an admin there is no
    # max os size for buffers, and benefits may be seen by tweaking the above.
    
    wrapped_object_name = 'socket'
    
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM,
                       proto=0, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(family, type, proto))        
        super(Socket, self).__init__(**kwargs)
        self._local_data = ''
        self.setblocking(self.blocking)
        self.settimeout(self.timeout)
        self.recv_size = self.os_recv_buffer_size
           
        if self.add_on_init:
            self.added_to_network = True
            try:
                objects["Network"].add(self)
            except KeyError:
                self.alert("Network component does not exist", level=0)
         
    def on_select(self):
        """ Used to customize behavior when a socket is readable according to select.select.
            It is less likely that one would overload this method; End users probably want
            to overload recv/recvfrom instead."""
        return self.recvfrom()
 
 #   @local_recvs
    def recv(self, buffer_size=0):
        """ Receives data from a remote endpoint. This method is event triggered and called
            when the socket becomes readable according to select.select. This
            method is called for Tcp sockets and requires a connection.
            
            Note that this recv will return the entire contents of the buffer and 
            does not need to be called in a loop."""
        if self._local_data:
            data = self._local_data
            self._local_data = bytes()
            return data
        
        buffer_size = buffer_size or self.recv_size 
        _memoryview = self._memoryview
        try:        
            while True:
                byte_count = self.socket.recv_into(_memoryview[self._byte_count:], 
                                                   buffer_size)                     
                if not byte_count:
                    break
                self._byte_count += byte_count                
        except (ValueError, socket.error) as error:        
            if isinstance(error, ValueError): # Socket._buffer is not big enough
                old_buffer = Socket._buffer
                del Socket._memoryview
                del _memoryview
                old_buffer.extend(bytearray(2 * len(old_buffer)))
                Socket._memoryview = memoryview(old_buffer)
                self.recv(buffer_size)                 
            elif error.errno != 10035:
                raise   
                
        _byte_count = self._byte_count
        self._byte_count = 0
        return bytes(self._buffer[:_byte_count])
        
    def recvfrom(self, buffer_size=0):
        """ Receives data from a host. For Udp sockets this method is event triggered
            and called when the socket becomes readable according to select.select. Subclasses
            should extend this method to customize functionality for when data is received."""
        byte_count, _from = self.socket.recvfrom_into(self._memoryview, 
                                                      buffer_size or self.recv_size)
        return bytes(self._buffer[:byte_count]), _from
    
    def send(self, data):
        """ Sends data to the connected endpoint. All of the data will be sent. """
        sockname = self.sockname
        peername = self.peername
        byte_count = len(data)
        
        if self.bypass_network_stack:
            if not self._endpoint_instance_name:
                if self.sockname in _socket_names: # socket is the client
                    self._endpoint_instance_name = _local_connections[self.sockname]
                else:
                    self._endpoint_instance_name = _socket_names[self.peername]
            self.alert("Bypassing network stack. Sending to {}", 
                       (self._endpoint_instance_name, ), level='vvv')
            instance = pride.objects[self._endpoint_instance_name]
            instance._local_data += data
            instance.recv()                 
        else:
            # send through the socket using the network stack
            _socket = self.socket
            _data = memoryview(data)
            
            position = 0
            while position < byte_count:
                sent = _socket.send(_data[position:])
                position += sent  
            return position
             
    def connect(self, address):
        """ Perform a non blocking connect to the specified address. The on_connect method
            is called when the connection succeeds, or the appropriate error handler method
            is called if the connection fails. Subclasses should overload on_connect instead
            of this method."""
        self.host_info = address
        try:
            self.wrapped_object.connect(address)
        except socket.error as error:
            if ERROR_CODES[error.errno] == "CONNECTION_IS_CONNECTED":
                self.on_connect()
            elif not self._connecting:
                self._connection_attempts = self.connection_attempts
                latency = self.latency = pride.utilities.Latency(size=10)
                latency.start_measuring()
                self._connecting = True
                objects["Network"].connecting.add(self)
            else:
                raise
        else:
            self.on_connect()
            
    def on_connect(self):
        """ Performs any logic required when a Tcp connection succeeds. This 
            method should be extended by subclasses."""
        #self.latency.finish_measuring()
        #buffer_size = round_trip_time * connection_bps # 100Mbps for default
        self.connected = True        
        self.peername = self.getpeername()
        self.sockname = self.getsockname()
        self.alert("Connected", level='v')
                
    def delete(self):
        if not self.closed:
            self.close()        
        #del _local_data[self]
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
        stats["connecting"] = False
        stats["_connected"] = False
        stats["added_to_network"] = False
        return stats
        
    def on_load(self, attributes):
        super(Socket, self).on_load(attributes)
        self.wraps(socket.socket(self.socket_family, self.socket_type, 
                                 self.protocol))
        self.setblocking(self.blocking)
        self.settimeout(self.timeout)
                
        if self.add_on_init:
            try:
                $Network.add(self)
            except KeyError: 
                self.alert("Network unavailable")
            else:
                self.added_to_network = True
                
                
class Raw_Socket(Socket):
    
    defaults = {"socket_type" : socket.SOCK_RAW,
                "protocol" : 0}
    
    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET, 
                                                          socket.SOCK_RAW, 
                                                          Raw_Socket.defaults["protocol"]))
        super(Raw_Socket, self).__init__(**kwargs)
        
        
class Packet_Sniffer(Raw_Socket):
            
    defaults = {"IP_HDRINCL" : 1}
    
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

    defaults = {"socket_family" : socket.AF_INET,
                "socket_type" : socket.SOCK_STREAM,
                "dont_save" : True}
    
    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET,
                                                          socket.SOCK_STREAM))
        self._local_data = bytes()
        super(Tcp_Socket, self).__init__(**kwargs)
                 
    def on_select(self):
        self.recv()
        
    def on_connect(self):
        super(Tcp_Socket, self).on_connect()
        _local_connections[self.peername] = self.instance_name
        try:
            self._endpoint_instance_name = _socket_names[self.peername]
        except KeyError:
            self._endpoint_instance_name = None
            
        
class Server(Tcp_Socket):

    defaults = {"port" : 80,
                "backlog" : 50,
                "reuse_port" : 0,
                "Tcp_Socket_type" : "network.Tcp_Socket",
                "allow_port_zero" : False,
                "dont_save" : False,
                "replace_reference_on_load" : True}

    parser_ignore = Tcp_Socket.parser_ignore + ("backlog", "reuse_port", 
                                                "Tcp_Socket_type",
                                                "allow_port_zero")
    
    def __init__(self, **kwargs):       
        super(Server, self).__init__(**kwargs)
#        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, self.reuse_port)
        self.bind((self.interface, self.port))
        self.listen(self.backlog)
                    
    def on_select(self):
        try:
            while True:
                self.accept()
        except socket.error as error:
            if error.errno != 10035:
                raise
                
    def accept(self):
        _socket, address = self.socket.accept()
        
        connection = self.create(self.Tcp_Socket_type,
                                 wrapped_object=_socket,
                                 peername=address)   
        if address[0] in ("127.0.0.1", "localhost"):
            _local_connections[address] = connection.instance_name   
            
        connection.on_connect()         
        return connection, address
    
    def on_connect(self, connection, address):
        pass
        
    def on_load(self, attributes):
        super(Server, self).on_load(attributes)
        self.bind((self.interface, self.port))
        self.listen(self.backlog)
        
        
class Tcp_Client(Tcp_Socket):

    defaults = {"ip" : "",
                "port" : 80,
                "host_info" : tuple(),
                "auto_connect" : True,
                "as_port" : 0}
    
    parser_ignore = Tcp_Socket.parser_ignore + ("host_info", "auto_connect", "as_port")
    
    def __init__(self, **kwargs):
        super(Tcp_Client, self).__init__(**kwargs)        
        if self.as_port:
            self.bind((self.interface, self.as_port))            
        if not self.host_info:
            if not self.ip:
                self.alert("Attempted to create Tcp_Client with no host ip or host_info", tuple(), 0)
            self.host_info = (self.ip, self.port)
            
        if self.auto_connect:
            self.connect(self.host_info)

    def on_connect(self):
        super(Tcp_Client, self).on_connect()      
        if self.peername[0] in ("localhost", "127.0.0.1"):
            _socket_names[self.sockname] = self.instance_name
            try:
                self._endpoint_instance_name = _local_connections[self.sockname]
            except KeyError:
                self._endpoint_instance_name = None
                
        
class Udp_Socket(Socket):

    defaults = {"bind_on_init" : True}
    #del defaults["connection_attempts"]

    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        super(Udp_Socket, self).__init__(**kwargs)        
               
        if self.bind_on_init:
            self.bind((self.interface, self.port))
            
        if not self.port:
            self.port = self.getsockname()[1]
        
        
class Multicast_Beacon(Udp_Socket):

    defaults = {"packet_ttl" : struct.pack("b", 127),
                "multicast_group" : "224.0.0.0",
                "multicast_port" : 1929}

    parser_ignore = Udp_Socket.parser_ignore + ("packet_ttl", )
    
    def __init__(self, **kwargs):
        super(Multicast_Beacon, self).__init__(**kwargs)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.packet_ttl)


class Multicast_Receiver(Udp_Socket):

    defaults = {"address" : "224.0.0.0"}

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
    defaults = {"number_of_sockets" : 0,
                "priority" : .01,
                "update_priority" : 5,
                "_updating" : False,
                "running" : False}
   
    error_handler = Socket_Error_Handler()
    
    def __init__(self, **kwargs):
        # minor optimization; pre allocated slices and ranges for
        # sliding through the socket list to sidestep the 500 
        # file descriptor limit that select has. Produces slice objects
        # for ranges 0-500, 500-1000, 1000-1500, etc, up to 50000.
        self._slice_mapping = dict((x, slice(x * 500, (500 + x * 500))) for 
                                    x in xrange(100))                        
        self.connecting = set()
        self.sockets = []
        super(Network, self).__init__(**kwargs)       
                
    def add(self, sock):
    #    print "adding sock: ", hex(id(sock))
        super(Network, self).add(sock)
        self.sockets.append(sock)
        if not self.running:
            self.running = True        
            self.start()
                
    def remove(self, sock):   
    #    print "\nremoving sock: ", hex(id(sock)), '\n'
        super(Network, self).remove(sock)
        self.sockets.remove(sock)
            
    def delete(self):
        super(Network, self).delete()
        del self.sockets
        del self.connecting
        
    def run(self):
        sockets = self.sockets
        if not sockets:
            self.running = False
        else:
            error_handler = objects["Socket_Error_Handler"]       
            readable, writable, empty_list = [], [], []
            # select has a max # of file descriptors it can handle, which
            # is about 500 (at least on windows). step through in slices (0, 500), (500, 100), ...           
            for socket_list in (sockets[self._slice_mapping[chunk_number]] for
                                chunk_number in xrange((len(sockets) / 500) + 1)): 
                (readable_sockets, 
                 writable_sockets, _) = select.select(socket_list, socket_list, 
                                                      empty_list, 0.0)
                if readable_sockets:
                    readable.extend(readable_sockets)                
                if writable_sockets:
                    writable.extend(writable_sockets)
                    
            if readable:
                for _socket in readable:
                    try:
                        _socket.on_select()
                    except socket.error as error:
                        self.alert("socket.error when reading on select: {}", error, level=0)
                        error_handler.dispatch(_socket, error, ERROR_CODES[error.errno].lower()) 
                        
            connecting = self.connecting
            self.connecting = set()    
            if connecting and writable:                            
                # if a connecting tcp client is now writable, it's connected   
                for accepted in connecting.intersection(writable):
                    accepted.on_connect()
                    
                # if not, then it's still waiting or the connection timed out
                still_connecting = connecting.difference(writable)
                for connection in still_connecting:
                    connection.connection_attempts -= 1
                    if not connection.connection_attempts:
                        try:
                            connection.connect(connection.host_info)
                        except socket.error as error:                           
                            error_handler.dispatch(connection, error, 
                                                   ERROR_CODES[error.errno].lower())           
                    else:
                        self.connecting.add(connection)                   
                
    def __getstate__(self):
        state = super(Network, self).__getstate__()
        state["connecting"] = None
     #   state["sockets"] = []
     #   state["objects"] = {}
        state["_slice_mapping"] = None
        return state
    
    def __contains__(self, _socket):
        return _socket in self.sockets
        
    def on_load(self, attributes):
        super(Network, self).on_load(attributes)
        self._slice_mapping = dict((x, slice(x * 500, (500 + x * 500))) for 
                                    x in xrange(100))
        self.connecting = set()
        #self.sockets = []
