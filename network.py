#   mpf.network_library - builds on sockets - basic authentication - asynchronous network
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
import sys
import os
import socket
import select
import struct
import errno
import time
import mmap
import contextlib
import traceback
import getpass
import functools
#import hashlib

import vmlibrary
import defaults
import base
from utilities import Latency, Average
Instruction = base.Instruction

try:
    CALL_WOULD_BLOCK = errno.WSAEWOULDBLOCK
    BAD_TARGET = errno.WSAEINVAL
    CONNECTION_IN_PROGRESS = errno.WSAEWOULDBLOCK
    CONNECTION_IS_CONNECTED = errno.WSAEISCONN
    CONNECTION_WAS_ABORTED = errno.WSAECONNABORTED
except:
    CALL_WOULD_BLOCK = errno.EWOULDBLOCK
    CONNECTION_IN_PROGRESS = errno.EINPROGRESS
    CONNECTION_IS_CONNECTED = errno.EISCONN
    CONNECTION_WAS_ABORTED = errno.ECONNABORTED

        
class Socket(base.Wrapper):

    defaults = defaults.Socket

    def _get_address(self):
        return (self.ip, self.port)
    address = property(_get_address)

    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket())
        self.network_buffer = {}
        super(Socket, self).__init__(**kwargs)
        self.setblocking(self.blocking)
        self.settimeout(self.timeout)
        if self.add_on_init:
            self.parallel_method("Asynchronous_Network", "add", self)
         
    def socket_recv(self):
        data, address = self.recvfrom(self.network_packet_size)
        try:
            self.network_buffer[address] += data
        except KeyError:
            self.network_buffer[address] = data
            
    def send_data(self, data, to=None):
        self.parallel_method("Asynchronous_Network", "send",
                           self, data, to)
                           
    def delete(self):
        self.close()        
        super(Socket, self).delete()
                            
        
class Connection(Socket):

    defaults = defaults.Connection

    def __init__(self, **kwargs):
        super(Connection, self).__init__(**kwargs)

    def socket_recv(self):
        self.network_buffer += self.recv(self.network_packet_size)

        
class Server(Connection):

    defaults = defaults.Server

    def __init__(self, **kwargs):
        self.client_options = {}
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

    def socket_recv(self):
        _socket, address = self.accept()
        
        connection = self.create(self.inbound_connection_type,
                                  wrapped_object=_socket,
                                  peer_address=address,
                                  **self.client_options)
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


class Outbound_Connection(Connection):

    defaults = defaults.Outbound_Connection

    def __init__(self, **kwargs):
        super(Outbound_Connection, self).__init__(**kwargs)
        
        if not self.target:
            if not self.ip:
                self.alert("Attempted to create Outbound_Connection with no host ip or target", tuple(), 0)
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
                #self.error_handler.get(error.errno, self.unhandled_error)()
                if error == CONNECTION_IS_CONNECTED: # complete
                    self.parallel_method("Asynchronous_Network", "add", self)
                    self.on_connect()

                elif error in (CALL_WOULD_BLOCK, CONNECTION_IN_PROGRESS): # waiting
                    self.alert("{0} waiting for connection to {1}", (self.instance_name, self.target), level="vv")
                    self.stop_connecting = False

                elif error == BAD_TARGET: #10022: # WSAEINVALID bad target
                    self.alert("WSAEINVALID bad target for {0}", [self.instance_name], level=self.bad_target_verbosity)
                    self.delete()

                else:
                    print "unhandled exception for", self.instance_name
                    print traceback.format_exc()
                    self.delete()
            else:
                self.on_connect(self)

        return self.stop_connecting
        

class Inbound_Connection(Connection):

    defaults = defaults.Inbound_Connection

    def __init__(self, **kwargs):
        super(Inbound_Connection, self).__init__(**kwargs)


class Udp_Socket(Socket):

    defaults = defaults.Udp_Socket

    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        super(Udp_Socket, self).__init__(**kwargs)        
        self.network_buffer = {}       
        
        self.bind((self.interface, self.port))
        if not self.port:
            self.port = self.getsockname()[1]
            
        self.settimeout(self.timeout)                       
             
        
        
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
        self.bind((self.listener_address, self.port))
        group_option = socket.inet_aton(self.multicast_group)
        multicast_configuration = struct.pack("4sL", group_option, socket.INADDR_ANY)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_configuration)


class Connection_Manager(vmlibrary.Process):

    defaults = defaults.Connection_Manager
    
    def _get_buffer(self):
        return self.objects[socket.socket.__name__]
    buffer = property(_get_buffer)
        
    def __init__(self, **kwargs):        
        super(Connection_Manager, self).__init__(**kwargs)
        self.objects[socket.socket.__name__] = []
        self.running = False
        
    def add(self, sock):
        self.running = True
        super(Connection_Manager, self).add(sock)
        
    def run(self):
        for connection in self.buffer:
            self.remove(connection)
            if not connection.deleted and not connection.attempt_connection():
                self.add(connection)          
        if not self.buffer:
            self.running = False
           

class Asynchronous_Network(vmlibrary.Process):

    defaults = defaults.Asynchronous_Network

    def _get_local_services(self):
        local_names = ("localhost", "0.0.0.0", "127.0.0.1")
        return dict((key, value) for key, value in self.services.items() if key in local_names)
    local_services = property(_get_local_services)
   
    def __init__(self, **kwargs):
        # minor optimization
        # pre allocated slices and ranges
        self._socket_name = socket.socket.__name__
        self._slice_mapping = dict((x, slice(x * 500, (500 + x * 500))) for x in xrange(10))
        self._socket_range_size = range(1)
        self._select = select.select

        self.write_buffer = {}
        self.writable = set()
        super(Asynchronous_Network, self).__init__(**kwargs)
        self.running = False
        self.objects[socket.socket.__name__] = []
                
        self.connection_manager = self.create(Connection_Manager)

        instruction = self.update_instruction = Instruction("Asynchronous_Network", "_update_range_size")        
        instruction.execute(self.update_priority)
  
    def add(self, sock):
        super(Asynchronous_Network, self).add(sock)
        if not self.running:
            self.run_instruction.execute(priority=self.priority)
            self.running = True
            
    def debuffer_data(self, connection):
        try:
            del self.write_buffer[connection]
        except KeyError:
            pass
        
    def _update_range_size(self):
        self._socket_range_size = range((len(self.objects[self._socket_name]) / 500) + 1)
        self.update_instruction.execute(self.update_priority)

    def run(self):
        if self.connection_manager.running:
            self.connection_manager.run()

        sockets = self.objects[self._socket_name]
        
        if sockets:
            self_writable = self.writable = set()
            for chunk in self._socket_range_size:
                # select has a max # of file descriptors it can handle, which
                # is about 500 (at least on windows). We can avoid this limitation
                # by sliding through the socket list in slices of 500 at a time
                socket_list = sockets[self._slice_mapping[chunk]]
                
                readable, writable, errors = self._select(socket_list, socket_list, [], 0.0)
                        
                self_writable.update(writable)
                
                if readable:
                    self.handle_reads(readable)                
            
            if self.handle_resends:
                resends = ((sock, self.write_buffer.pop(sock)) for sock, messages in
                            self.write_buffer.items() if sock in self_writable)
                    
                for sender, messages in resends:
                    for message, to in messages:
                        self.send(sender, message, to)
            
            self.run_instruction.execute(priority=self.priority)
            
    def handle_reads(self, readable_sockets):
        for sock in readable_sockets:
            try:
                sock.socket_recv()
            except socket.error as error:
                if error.errno == CONNECTION_WAS_ABORTED:
                    sock.close()
                    sock.delete()
                elif error.errno == 11: # EAGAIN on unix
                    self.alert("EAGAIN error reading {0}",
                              (sock, ), 0)
                else:
                    raise
                    
    def send(self, sock, data, to=None):   
        if sock in self.writable:
            if to:

                sock.sendto(data, to)
            else:
                sock.send(data)            
        else:
            self.handle_resends = True
            if to:
                data = (data, to)
            else:
                data = (data, None)
            try:
                self.write_buffer[sock].append(data)
            except KeyError:
                self.write_buffer[sock] = [data]            