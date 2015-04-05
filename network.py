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

ERROR_CODES = {}
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
        sock.handle_connection_reset()
        
    def connection_was_aborted(self, sock, error):
        sock.close()
        sock.delete()
        
    def eagain(self, sock, error):
        sock.alert("{}", [error], level=0)
        
    def unhandled(self, sock, error):
        sock.alert("Unhandled error:\n{}", [error], level=0)
        
        
class Socket(base.Wrapper):

    defaults = defaults.Socket

    def _get_recv_method(self):
        return self.recvfrom
    _network_recv = property(_get_recv_method)
    
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
         
    def send(self, data):
        return self.parallel_method("Network", "send", self, data)
                             
    def sendto(self, data, host_info):
        return self.parallel_method("Network", "sendto", 
                                    self, data, host_info)
    def recv(self, buffer_size=0):
        buffer_size = (self.network_packet_size if not buffer_size else
                       buffer_size)
        return self.wrapped_object.recv(buffer_size)
        
    def recvfrom(self, buffer_size=0):
        buffer_size = (self.network_packet_size if not buffer_size else
                       buffer_size)
        return self.wrapped_object.recvfrom(buffer_size)
        
    def delete(self):
        self.close()        
        super(Socket, self).delete()
    
    def close(self):
        if self.added_to_network:
            self.parallel_method("Network", "remove", self)
        self.wrapped_object.close()
        
       
class Tcp_Socket(Socket):

    defaults = defaults.Tcp_Socket
    
    def _get_recv_method(self):
        return self.recv
    _network_recv = property(_get_recv_method)
    
    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET,
                                                          socket.SOCK_STREAM))
        super(Tcp_Socket, self).__init__(**kwargs)

        
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
        
        self.parallel_method("Connection_Manager", "add", self)
                
    def unhandled_error(self):
        print "unhandled exception for", self.instance_name
        self.delete()

    def attempt_connection(self):
        self.stop_connecting = True
        if not self.connect_attempts:
            self.alert("{0} to {1} timed out after {2} frames", (self.instance_name, self.target, self.timeout), 0)
            self.delete()

        else:
            self.connect_attempts -= 1
            try: # non blocking connect
                self.connect(self.target)
            except socket.error as socket_error:
                error = socket_error.errno
                
                if error == CONNECTION_IS_CONNECTED: # complete
                    self.parallel_method("Network", "add", self)
                    self.added_to_network = True
                    self.on_connect()                    
                                        
                elif error in (CALL_WOULD_BLOCK, CONNECTION_IN_PROGRESS): # waiting
                    self.alert("waiting for connection to {}", (self.target, ), level="vv")
                    self.stop_connecting = False

                elif error == BAD_TARGET: #10022: # WSAEINVALID bad target
                    self.alert("WSAEINVALID bad target", [self.instance_name], level=self.bad_target_verbosity)
                    self.delete()
                    
                else:
                    print "unhandled exception for", self.instance_name
                    print traceback.format_exc()
                    self.delete()
            else:
                self.added_to_network = True
                self.on_connect()                
                
        return self.stop_connecting
        
    def on_connect(self):
        raise NotImplementedError
        
        
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


class Connection_Manager(vmlibrary.Process):

    defaults = defaults.Connection_Manager
        
    def __init__(self, **kwargs):        
        super(Connection_Manager, self).__init__(**kwargs)
        self.buffer = []
        self.running = False
        
    def add(self, sock):
        self.running = True
        self.buffer.append(sock)
        self.parallel_method("Network", "_run")
        
    def run(self):
        running = False
        buffer = self.buffer
        new_buffer = self.buffer = []
        while buffer:
            
            connection = buffer.pop()     
            if not connection.deleted and not connection.attempt_connection():
                running = True
                new_buffer.append(connection)          
        
        self.running = running
           

class Network(vmlibrary.Process):

    defaults = defaults.Network
   
    def __init__(self, **kwargs):
        # minor optimization; pre allocated slices and ranges for
        # sliding through the socket list to sidestep the 500 
        # file descriptor limit that select has. Produces slice objects
        # for ranges 0-500, 500-1000, 1000-1500, etc, up to 5000.
        self._slice_mapping = dict((x, slice(x * 500, (500 + x * 500))) for 
                                    x in xrange(10))
        self._socket_range_size = range(1)
        
        self.send_buffer = {}
        self.sendto_buffer = {}
        self.writable = set()
        super(Network, self).__init__(**kwargs)
        self.sockets = self.objects["Socket_Objects"] = []
        self.late_sends = self.delayed_sendtos = self.delayed_sends = self.running = False
                        
        self.connection_manager = self.create(Connection_Manager)
        self.sockets.remove(self.connection_manager)
        
        instruction = self.update_instruction = Instruction("Network", "_update_range_size")        
        instruction.execute(self.update_priority)
  
    def add(self, sock):
        super(Network, self).add(sock)
        self.sockets.append(sock)
        self._run()
    
    def remove(self, sock):
        super(Network, self).remove(sock)
        self.sockets.remove(sock)
        
    def _run(self):
        if not self.running:
            self.run_instruction.execute(priority=self.priority)
            self.running = True
                   
    def _update_range_size(self):
        self._socket_range_size = range((len(self.sockets) / 500) + 1)
        self.update_instruction.execute(self.update_priority)

    def run(self):
        if self.connection_manager.running:
            self.connection_manager.run()
        
        sockets = self.sockets
        
        if sockets:
            for chunk in self._socket_range_size:
                # select has a max # of file descriptors it can handle, which
                # is about 500 (at least on windows). We can avoid this limitation
                # by sliding through the socket list in slices of 500 at a time
                socket_list = sockets[self._slice_mapping[chunk]]

                readable, writable, errors = select.select(socket_list, socket_list, [], 0.0)
                
                self.writable = writable
                
                if readable:
                    self.handle_reads(readable)                

            if self.late_sends:
                self.handle_delayed_sends(writable)
                                        
            self.run_instruction.execute(priority=self.priority)
        else:
            self.running = False
       
    def handle_delayed_sends(self, writable):
        self.late_sends = False
        if self.delayed_sends:
            self.delayed_sends = False
            resends = ((sock, self.send_buffer.pop(sock)) for sock, messages in
                        self.send_buffer.items() if sock in writable)
            self.alert("sending delayed tcp sends", level=0)
            
            for sender, messages in resends:
                for data in messages:
                    self.alert("Sending {} on {}",
                               [data[:128], sender],
                               level=0)
                    self.send(sender, data)
        
        if self.delayed_sendtos:
            self.delayed_sendtos = False
            resends = ((sock, self.sendto_buffer.pop(sock)) for sock, message in
                        self.sendto_buffer.items() if sock in writable)
            self.alert("sending delayed udp sendto's", level=0)
            
            for sender, messages in resends:
                for data, host_info in messages:
                    self.sendto(sender, data, host_info)
                    
    def handle_reads(self, readable_sockets):
        for sock in readable_sockets:
            try:
                sock._network_recv()
            except socket.error as error:       
                handler = getattr(sock.error_handler, 
                                  ERROR_CODES[error.errno].lower(),
                                  sock.error_handler.unhandled)
                    
    def send(self, sock, data):   
        if sock in self.writable:
            byte_count = sock.wrapped_object.send(data)          
        else:
            self.alert("{} not writable; delaying send of {} bytes",
                       (sock.instance_name, len(data)),
                       level=0)
                       
            self.late_sends = self.delayed_sends = True
            byte_count = 0
            try:
                self.send_buffer[sock].append(data)
            except KeyError:
                self.send_buffer[sock] = [data]
        return byte_count
        
    def sendto(self, sock, data, host_info):
        if sock in self.writable:
            byte_count = sock.wrapped_object.sendto(data, host_info)
        else:
            self.alert("{} not writable; delaying send of {} bytes",
                       (sock.instance_name, len(data)),
                       level=0)
                       
            self.late_sends = self.delayed_sendtos = True
            delayed_sendto = (data, host_info)
            byte_count = 0
            try:
                self.sendto_buffer[sock].append(delayed_sendto)
            except KeyError:
                self.sendto_buffer[sock] = [delayed_sendto]
        return byte_count