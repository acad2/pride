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
        super(Socket, self).__init__(**kwargs)
        self.setblocking(self.blocking)
        self.settimeout(self.timeout)
        if self.add_on_init:
            self.public_method("Asynchronous_Network", "add", self)
    
    def delete(self):
        self.close()        
        super(Socket, self).delete()
     
    def socket_send(self, data):
        target, message = data
        self.sendto(message, target)
                
    def handle_idle(self):
        if not self.deleted:
            if self.idle:
                self.alert("{0} idle disconnect after {1}s", (self.instance_name, self.timeout_after), 0)
                self.delete()
            else:
                self.idle = True
                self.idle_instruction.execute()
        
        
class Connection(Socket):

    defaults = defaults.Connection

    def __init__(self, **kwargs):
        super(Connection, self).__init__(**kwargs)

    def socket_recv(self):
        self.network_buffer += self.recv(self.network_packet_size)
        
    def socket_send(self, data):
        self.send(data)
                

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

        self.public_method("Connection_Manager", "add", self)
                
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
                    self.public_method("Asynchronous_Network", "add", self)
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
             
    def socket_recv(self):
        data, address = self.recvfrom(self.network_packet_size)
        try:
            self.network_buffer[address] += data
        except KeyError:
            self.network_buffer[address] = data
        
        
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


class Basic_Authentication_Client(vmlibrary.Thread):

    defaults = defaults.Basic_Authentication_Client

    def __init__(self, **kwargs):
        self.username = ''
        self.password = ''
        self.auto_login = None
        super(Basic_Authentication_Client, self).__init__(**kwargs)
        self.thread = self._new_thread()
        instruction = self.wait_instruction = Instruction(self.instance_name, "wait")

    def run(self):
        try:
            next(self.thread)
        except StopIteration:
            self.delete()

    def wait(self):
        self.alert("\t{0} waiting for reply", [self.instance_name], level="vvv")
        
    def _new_thread(self):
        connection = self.connection
        
        username = self.username
        password = self.password
        if username:
            if password:
                self.alert("Attempting to automatically log in as {0}...",
                          (username, ), "v")
            else:
                password = getpass.getpass()
        else:
            username = self.username if self.username else\
                       raw_input("Please provide credentials for {0}\nUsername: "\
                                 .format(self.instance_name))
            password = password if password else getpass.getpass()

        password = hash(password) # WARNING: not seriously secure!
        response = username+"\n"+str(password)

        connection.rpc(response)
        self.wait()
        yield
        
        messages = connection.read_messages()
        while not messages:
            self.wait()
            yield
            messages = connection.read_messages()
        
        reply = messages[0][1].lower()
        
        if reply in ("invalid password", "invalid username"):
            self.alert("{0} supplied in login attempt",
                      (reply, ), 0)
            if reply == "invalid password":
                self.handle_invalid_password()
            else:
                self.handle_invalid_username()
        else:
            self.handle_success(reply)

    def retry(self):
        if "y" in raw_input("Retry?: ").lower():
            self.login_thread = self._new_thread()
            sefl.wait()
        else:
            self.alert("failed to login. Exiting...", level=0)

    def handle_invalid_username(self):
        self.retry()

    def handle_invalid_password(self):
        self.retry()

    def handle_success(self, reply=''):
        Instruction(self.parent, "login_success", reply).execute()


class Connection_Manager(vmlibrary.Thread):

    defaults = defaults.Thread.copy()
    
    def _get_buffer(self):
        return self.objects[socket.socket.__name__]
    buffer = property(_get_buffer)
    
    public_methods = ("add", )
    
    def __init__(self, **kwargs):        
        super(Connection_Manager, self).__init__(**kwargs)
        self.objects[socket.socket.__name__] = []
        self.thread = self._new_thread()
       # self.running = False
 
    def run(self):
        return next(self.thread)

    def _new_thread(self):
        buffer = self.buffer
        while True:        
            for connection in buffer:
                self.remove(connection)
                if not connection.deleted and not connection.attempt_connection():
                    self.add(connection)          
            yield
           

class Asynchronous_Network(vmlibrary.Process):

    defaults = defaults.Asynchronous_Network

    def _get_local_services(self):
        local_names = ("localhost", "0.0.0.0", "127.0.0.1")
        return dict((key, value) for key, value in self.services.items() if key in local_names)
    local_services = property(_get_local_services)

    public_methods = ("buffer_data", "add")
    
    def __init__(self, **kwargs):
        # minor optimization
        # pre allocated slices and ranges
        self._socket_name = socket.socket.__name__
        self._slice_mapping = dict((x, slice(x * 500, (500 + x * 500))) for x in xrange(10))
        self._socket_range_size = range(1)
        self._select = select.select

        self.write_buffer = {}
        super(Asynchronous_Network, self).__init__(**kwargs)
        self.objects[socket.socket.__name__] = []
                
        self.connection_manager = self.create(Connection_Manager)

        instruction = self.update_instruction = Instruction("Asynchronous_Network", "_update_range_size")
        instruction.priority = self.update_priority
        instruction.execute()

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
        
    def _update_range_size(self):
        self._socket_range_size = range((len(self.objects[self._socket_name]) / 500) + 1)
        self.update_instruction.execute()

    def run(self):
        self.run_instruction.execute()
        self.connection_manager.run()

        sockets = self.objects[self._socket_name]
        for chunk in self._socket_range_size:
            # select has a max # of file descriptors it can handle, which
            # is about 500 (at least on windows). We can avoid this limitation
            # by sliding through the socket list in slices of 500 at a time
            socket_list = sockets[self._slice_mapping[chunk]]

            readable, writable, errors = self._select(socket_list, socket_list, [], 0.0)
            if readable:
                self.handle_reads(readable)
                
            if writable:
                needs_write = ((sock, self.write_buffer.pop(sock)) for sock in 
                                self.write_buffer.keys() if sock in writable)     
                self.handle_writes(needs_write)

    def handle_errors(self, socket_list):
        self.alert("Encountered sockets with errors", level=0)

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

    def handle_writes(self, writable_sockets):
        for sock, messages in writable_sockets:
            try:
                for message in messages:                   
                    sock.socket_send(message)
            except socket.error as error:            
                if error.errno == CONNECTION_WAS_ABORTED:
                    self.alert("Failed to send {0} on {1}\n{2}",
                          (message, sock, error), 0)
                    sock.delete()
                    
                elif error.errno == 11: # EAGAIN on unix
                    self.alert("EAGAIN error when writing to {0}",
                            (sock, ), 0)
                else:
                    raise