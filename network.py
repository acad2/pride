#   pride.network - Asynchronous socket operations
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

import pride
import pride.datastructures
import pride.vmlibrary as vmlibrary
import pride.base as base
import pride.utilities

ERROR_CODES = {}

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
                    CONNECTION_CLOSED : "CONNECTION_CLOSED",
                    11001 : "GETADDRINFO_FAILED"}) # not in errno.errorcode
               
HOST = socket.gethostbyname(socket.gethostname())
  
class Socket_Error_Handler(pride.base.Base):       
                 
    def dispatch(self, sock, error, error_name):        
        sock.alert("socket.error: {}".format(error), 
                  level=sock.verbosity.get(error_name, sock.verbosity["unhandled"]))
        sock.delete()
                
       
class Socket(base.Wrapper):
    """ Provides a mostly transparent asynchronous socket interface by applying a 
        Wrapper to a _socketobject. The default socket family is socket.AF_INET and
        the default socket type is socket.SOCK_STREAM (a tcp socket)."""
    defaults = {# standard socket stuff; see respective documentation for more information
                "socket_family" : socket.AF_INET, "socket_type" : socket.SOCK_STREAM,
                "protocol" : socket.IPPROTO_IP,
                "interface" : "0.0.0.0", "port" : 0,
                
                # if timeout is not 0, then settimeout is called when initializing
                # otherwise setblocking is called.
                "blocking" : 0, "timeout" : 0,                                
                
                # connect_timeout is how long, in seconds, to wait before giving up when
                # when attempting to establish a new connection to a server. 
                "connect_timeout" : 1,
                                                
                # Sockets that are connected to each other from within the application
                # can communicate directly with each other via references, bypassing
                # even the loopback connector; 0 round trips occur, all sends/recvs occur inline
                "bypass_network_stack" : True,
                "shutdown_on_close" : True, "shutdown_flag" : 2}
        
    additional_parser_ignores = defaults.keys()
    additional_parser_ignores.remove("interface")
    additional_parser_ignores.remove("port")
    parser_ignore = tuple(additional_parser_ignores)
    
    flags = {"_byte_count" : 0, "_connecting" : False, "_endpoint_reference" : '',
             "connected" : False, "closed" : False, "_local_data" : '',
             "_saved_in_attribute" : ''}
    
    verbosity = {"close" : "socket_close", "network_nonexistant" : "vv",
                 "recv_eof" : "vv", "connected" : "vv",
                 
                 "call_would_block" : 'vv', "connection_in_progress" : "vv",
                 "connection_closed" : "vv", "connection_reset" : "vv",
                 "connection_was_aborted" : "vv", "eagain" : "vv",
                 "bad_target" : "vv", "unhandled" : 0, "bind_error" : 0,
                 "getaddrinfo_failed" : 0}
    
    _buffer = bytearray(1024 * 1024)
    _memoryview = memoryview(_buffer)
    
    def _get_address(self):
        return (self.ip, self.port)
    address = property(_get_address)
    
    def _get_os_recv_buffer_size(self):
        return self.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)        
    def _set_os_recv_buffer_size(self, size):
        self.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, size)
        Socket.recv_size = self.os_recv_buffer_size
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
    
    # so we only have to set it once instead of for every instance initialized
    __socket = socket.socket()
    recv_size = __socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    __socket.close()
    del __socket
    
    wrapped_object_name = 'socket'
    
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM,
                       proto=0, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(family, type, proto))        
        super(Socket, self).__init__(**kwargs)
        
        if self.timeout:            
            self.settimeout(self.timeout) 
        else:
            self.setblocking(self.blocking)           
        try:
            objects["->Python->Network"].add(self)
        except KeyError:
            self.alert("Network component does not exist", 
                       level=self.verbosity["network_nonexistant"])
         
    def on_select(self):
        """ Used to customize behavior when a socket is readable according to select.select.
            It is less likely that one would overload this method; End users probably want
            to overload recv/recvfrom instead."""
        return self.recv()
  
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
                    if not self._byte_count:
                        self.alert("Received EOF", level=self.verbosity["recv_eof"])
                        self.shutdown_on_close = False
                        error = socket.error(CONNECTION_CLOSED)
                        error.errno = CONNECTION_CLOSED
                        raise error
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
#        assert not self.deleted 
#        assert not self.closed
        if self.bypass_network_stack:
            if not self._endpoint_reference:                
                self._endpoint_reference = pride.objects["->Python->Network_Connection_Manager"].socket_reference[self.peername]
            instance = pride.objects[self._endpoint_reference]
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
                self._started_connecting_at = pride.utilities.timer_function()
                #self.latency = pride.datastructures.Latency(size=10)
                self._connecting = True
                objects["->Python->Network"].connecting.add(self)
            else:
                raise
        else:
            self.on_connect()
            
    def on_connect(self):
        """ Performs any logic required when a Tcp connection succeeds. This 
            method should be extended by subclasses."""
        #self.latency.mark()
        #buffer_size = round_trip_time * connection_bps # 100Mbps for default
        self.connected = True        
        self.peername = self.getpeername()
        self.sockname = self.getsockname()
        self.alert("Connected", level=self.verbosity["connected"])
                
    def delete(self):
        if not self.closed:
            self.close()        
        super(Socket, self).delete()
    
    def close(self):
        self.alert("Closing", level=self.verbosity["close"])
    #    objects["->Python->Network"].remove(self)
        if self._saved_in_attribute:
            connection_manager = objects["->Python->Network_Connection_Manager"]
            sockname = self.sockname
            #import pprint
            #print self, "Removing from connection manager"
            #pprint.pprint(connection_manager.inbound_connections)
            #pprint.pprint(connection_manager.outbound_connections)
            
            del getattr(connection_manager, self._saved_in_attribute)[sockname]
            del connection_manager.socket_reference[sockname]
        if self.shutdown_on_close and self.connected:
            self.wrapped_object.shutdown(self.shutdown_flag)
        self.wrapped_object.close()
        self.closed = True
    
    def __getstate__(self):
        stats = super(Socket, self).__getstate__()
        del stats["wrapped_object"]
        del stats["socket"]
        stats["connecting"] = False
        stats["_connected"] = False        
        return stats
        
    def on_load(self, attributes):
        super(Socket, self).on_load(attributes)
        self.wraps(socket.socket(self.socket_family, self.socket_type, 
                                 self.protocol))
        self.setblocking(self.blocking)
        self.settimeout(self.timeout)                
        
        try:
            pride.objects["->Python->Network"].add(self)
        except KeyError: 
            self.alert("Network unavailable")
            
                
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

    defaults = {"socket_family" : socket.AF_INET, "socket_type" : socket.SOCK_STREAM,
                "dont_save" : True}
    flags = {"_local_data" : b''}
                     
    def on_connect(self):
        super(Tcp_Socket, self).on_connect()
        connection_manager = pride.objects["->Python->Network_Connection_Manager"]
        sockname = self.sockname
        connection_manager.socket_reference[sockname] = self.reference
        connection_manager.inbound_connections[sockname] = self.peername
        self._saved_in_attribute = "inbound_connections"
            
        
class Server(Tcp_Socket):

    defaults = {"port" : 80,
                "backlog" : 50,
                "reuse_port" : 0,
                "Tcp_Socket_type" : "network.Tcp_Socket",
                "allow_port_zero" : False,
                "dont_save" : False,
                "replace_reference_on_load" : True,
                "shutdown_on_close" : False}

    parser_ignore = Tcp_Socket.parser_ignore + ("backlog", "reuse_port", 
                                                "Tcp_Socket_type",
                                                "allow_port_zero")
    
    def __init__(self, **kwargs):       
        super(Server, self).__init__(**kwargs)
#        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, self.reuse_port)
        self.bind((self.interface, self.port))
        self.listen(self.backlog)
        pride.objects["->Python->Network_Connection_Manager"].servers[(self.interface, self.port)] = self.reference
        
    def on_select(self):
        try:
            while True:
                self.accept()
        except socket.error as error:
            if error.errno != 10035:
                raise
                
    def accept(self):
        _socket, address = self.socket.accept()
        
        connection = self.create(self.Tcp_Socket_type, wrapped_object=_socket,
                                 peername=address)   
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
        connection_manager = objects["->Python->Network_Connection_Manager"]
        sockname = self.sockname
        connection_manager.socket_reference[sockname] = self.reference
        connection_manager.outbound_connections[sockname] = self.peername
        self._saved_in_attribute = "outbound_connections"
        
        
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
        
    def on_select(self):
        return self.recvfrom()
        
        
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
           

class Network_Connection_Manager(pride.base.Base):
    """ Provides a record of sockets currently in use. 
    
        The inbound and outbound connections dictionary maps (ip, port) pairs
        to the (ip, port) pair of their connected endpoint 
        
        The socket_reference dictionary maps socket (ip, port) pairs to the 
        socket.reference. This applies to local sockets only. The reference 
        can be/is used to bypass the network stack and call send/recv between
        sockets exclusively at the application level. 
        
        The servers dictionary maps an (interface, port) pair to the reference
        of the server listening on at that address. """
    mutable_defaults = {"outbound_connections" : dict, "inbound_connections" : dict,
                        "servers" : dict, "socket_reference" : dict}            
        
        
class Network(vmlibrary.Process):
    """ Manages socket objects and is responsible for calling select.select to determine
        readability/writability of sockets. Also responsible for non blocking connect logic. 
        This component is created by default upon application startup, and in most cases will
        not require user interaction."""
    defaults = {"priority" : .01, "run_condition" : "sockets"}
   
    mutable_defaults = {"connecting" : set, "sockets" : list, 
                        "_timestamp" : pride.utilities.timer_function,
                        "error_handler" : Socket_Error_Handler}          
        
    def add(self, sock):
        super(Network, self).add(sock)
        self.sockets.append(sock)
                
    def remove(self, sock):   
        super(Network, self).remove(sock)
        self.sockets.remove(sock)
            
    def delete(self):
        super(Network, self).delete()
        del self.sockets
        del self.connecting
        
    def run(self):
        error_handler = self.error_handler
        readable, writable, empty_list = [], [], []
        # select has a max # of file descriptors it can handle, which
        # is about 500 (at least on windows). step through in slices (0, 500), (500, 100), ...           
        for socket_list in slide(self.sockets, 500): 
            (readable_sockets, 
             writable_sockets, _) = select.select(socket_list, socket_list, 
                                                  empty_list, 0.0)
            if readable_sockets:
                readable.extend(readable_sockets)                
            if writable_sockets:
                writable.extend(writable_sockets)
                
        connecting = self.connecting
        self.connecting = set()                 
        read_progress = 0
        readable_count = len(readable)
        # nesting the for within the while so we don't have to
        # set up and tear down a try... finally block for every socket        
        while read_progress < readable_count:
            try:
                for read_counter, _socket in enumerate(readable[read_progress:]):
                    _socket.on_select()                             
            except socket.error as error:                
                read_progress += (read_counter + 1)                               
                error_handler.dispatch(_socket, error, ERROR_CODES[error.errno].lower())
            except Exception as error:                
                _socket = readable[read_progress + read_counter]
                _socket.alert("Caught non socket.error during recv: {}", (error, ), level=0)                
                _socket.delete()
                read_progress += (read_counter + 1)
                readable_count -= 1                
            else:                
                break        
        
        if connecting and writable:                            
            # if a connecting tcp client is now writable, it's connected   
            for accepted in connecting.intersection(writable):
                accepted.on_connect()
                
            # if not, then it's still waiting or the connection timed out
            still_connecting = connecting.difference(writable)
            elapsed_time = self.priority
            
            old_timestamp = self._timestamp
            self._timestamp = now = pride.utilities.timer_function()
            elapsed_time = now - old_timestamp
            
            for connection in still_connecting:
                if now - connection._started_connecting_at > connection.connect_timeout:           
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
