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
#import hashlib

import vmlibrary
import defaults
import base
from utilities import Latency, Average
Event = base.Event

try:
    CONNECTION_IN_PROGRESS = errno.WSAEWOULDBLOCK
    CONNECTION_IS_CONNECTED = errno.WSAEISCONN
    CONNECTION_WAS_ABORTED = errno.WSAECONNABORTED
except:
    CONNECTION_IN_PROGRESS = errno.EINPROGRESS
    CONNECTION_IS_CONNECTED = errno.EISCONN
    CONNECTION_WAS_ABORTED = errno.ECONNABORTED
    
    
class Socket(base.Wrapper):
    
    defaults = defaults.Socket
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
        
    def _get_address(self):
        return (self.ip, self.port)
    address = property(_get_address)
    
    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket())    
        super(Socket, self).__init__(**kwargs)
        self.setblocking(0)
        if self.idle_check_interval:
            options = {"component" : self,
                       "priority" : self.idle_check_interval}
            Event(self.instance_name, "handle_idle", **options).post()
            
    def delete(self):      
        self.close()
        super(Socket, self).delete()

    def handle_idle(self):
        interval = self.idle_check_interval
        if self.idle:
            self.alert("{0} idle disconnect after {1}s", (self.instance_name, interval), 0)
            self.delete()
        else:
            self.idle = True
            event = Event(self.instance_name, "handle_idle", component=self).post()
            event.priority = interval
            
class Connection(Socket):
    
    defaults = defaults.Connection

    def __init__(self, **kwargs):
        super(Connection, self).__init__(**kwargs)
               
        
class Server(Connection):
    """usage: Event("Asynchronous_Network", "create", "networklibrary.Server",
    incoming=myincoming, outgoing=myoutgoing, on_connection=myonconnection,
    name="My_Server", port=40010).post()"""
    
    defaults = defaults.Server
    
    def __init__(self, **kwargs):
        self.inbound_connection_options = {}
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
            Event("Asynchronous_Network", "add_service", (self.interface, self.port), self.name).post()
            
    def handle_accept(self, server):
        connection, address = server.accept() # inbound connection received         
        
        options = server.inbound_connection_options
        options["wrapped_object"] = connection            
        
        for method in server.share_methods:
            options[method] = getattr(server, method)
        
        _connection = self.create(server.inbound_connection_type, **options)             
        Event("Asynchronous_Network", "add", _connection).post()        
        
        if server.on_connection: # server method to apply upon connection
            server.on_connection(_connection, address)
            
    def handle_bind_error(self):
        if self.allow_port_zero:
            self.bind((self.interface, 0))
            return True
        else:
            self.alert("{0}\nAddress already in use. Deleting {1}\n",
                       (traceback.format_exc(), self.instance_name), 0)        
            Event("Server", "delete", component=self).post()
        
        
class Outbound_Connection(Connection):
    
    defaults = defaults.Outbound_Connection
    
    def __init__(self, **kwargs):
        super(Outbound_Connection, self).__init__(**kwargs)    
        if not self.target:
            self.target = (self.ip, self.port)
        Event("Asynchronous_Network", "buffer_connection", self, self.target).post()
               
        
class Inbound_Connection(Connection):
    
    defaults = defaults.Inbound_Connection
    
    def __init__(self, **kwargs):
        super(Inbound_Connection, self).__init__(**kwargs)
                             
        
class UDP_Socket(Socket):
            
    defaults = defaults.UDP_Socket
    
    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        super(UDP_Socket, self).__init__(**kwargs)
        self.bind((self.interface, self.port))
        self.settimeout(self.timeout)
            
    
class Multicast_Beacon(UDP_Socket):
    
    defaults = defaults.Multicast_Beacon
    
    def __init__(self, **kwargs):
        super(Multicast_Beacon, self).__init__(**kwargs)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.packet_ttl)

        
class Multicast_Receiver(UDP_Socket):
    
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
        super(Basic_Authentication_Client, self).__init__(**kwargs)
        self.thread = self._new_thread()
        
    def run(self):
        try:
            next(self.thread)
        except StopIteration:
            self.delete()
 
    def wait(self):
        self.alert("Waiting for reply", level="vvv")
        
    def _new_thread(self):
        if self.auto_login:
            username, password = self.credentials
            self.alert("Attempting to automatically log in as {0}...",
                       (username, ), "v")          
        else:
            username = raw_input("Please provide credentials for {0}\nUsername: "\
                                 .format(self.instance_name))
            password = getpass.getpass()
        
        password = hash(password)
        response = username+"\n"+str(password)
        Event("Asynchronous_Network", "buffer_data", self.parent.connection, response).post()
        self.wait()
        yield
        
        while not self.parent.network_buffer:
            self.wait()
            yield            
            
        reply = self.parent.network_buffer.lower()
        if reply in ("invalid password", "invalid username"):
            self.alert("{0} supplied in login attempt",
                      (reply, ), 0)        
            if reply == "invalid password":
                self.handle_invalid_password()
            else:
                self.handle_invalid_username()
        else:
            self.handle_success(self.parent.connection)
            
    def retry(self):
        if "y" in raw_input("Retry?: ").lower():
            target = self.parent.connection.getpeername()
            raise NotImplementedError
            Event("Asynchronous_Network", "create", "networklibrary.Outbound_Connection",\
            target, incoming=self.incoming, outgoing=self.outgoing,\
            on_connection=self.on_connection).post()                
            #Event("Asynchronous_Network", "disconnect", self.connection).post()
        else:
            self.alert("failed to login. Exiting...", level=0)
                        
    def handle_invalid_username(self):
        self.retry()
        
    def handle_invalid_password(self):
        self.retry()
    
    def handle_success(self, connection):
        raise NotImplementedError
                
                
class Basic_Authentication(vmlibrary.Thread):
                    
    defaults = defaults.Basic_Authentication
    
    def __init__(self, connection, address, **kwargs):
        super(Basic_Authentication, self).__init__(**kwargs)
        self.thread = self._new_thread()
        self.connection = connection
        self.address = address
        
    def run(self):
        try:
            next(self.thread)
        except (AssertionError, KeyError, StopIteration) as exception:
            switch = {AssertionError : self.handle_invalid_password,
                      KeyError : self.handle_invalid_username,
                      StopIteration : self.handle_success}
            switch[type(exception)](self.connection, self.address)
            self.connection = None
            self.delete()
            
    def _new_thread(self):
        connection = self.connection
        while not self.parent.network_buffer[connection]:
            self.alert("waiting for reply", level="vvv")
            yield 
        self.alert("credentials received", level="vv")
        username, password = self.parent.network_buffer.pop(connection).strip().split("\n", 1)
        connection.username = username
        assert self.parent.authenticate[username] == int(password)
            
    def handle_invalid_username(self, connection, address):
        Event("Asynchronous_Network", "buffer_data", connection, self.invalid_username_string).post()
                
    def handle_invalid_password(self, connection, address):
        Event("Asynchronous_Network", "buffer_data", self.connection, self.invalid_password_string).post()
                
    def handle_success(self, connection, address):
        Event(self.parent, "log_in", connection).post()
        
    def delete(self):
        self.connection = None
        super(Basic_Authentication, self).delete()
        
        
class Asynchronous_Network(vmlibrary.Process):

    defaults = defaults.Asynchronous_Network
  
    def _get_local_services(self):
        local_names = ("localhost", "0.0.0.0", "127.0.0.1")
        return dict((key, value) for key, value in self.services.items() if key in local_names)        
    local_services = property(_get_local_services)
      
    def __init__(self, **kwargs):
        super(Asynchronous_Network, self).__init__(**kwargs)
        self.services = {}
        self.timeouts = {}
        self.write_buffer = {}
        self.connection_buffer = {}
        self.objects[socket.socket.__name__] = [] # pre allocate to avoid KeyError

    def add_service(self, address, service=''):
        if not service:
            host_name, port = address        
            try:
                service = socket.getservbyport(port)
            except socket.error:
                service = "Unknown"
        self.services[address] = service
        
    def remove_service(self, address):
        del self.services[address]
        
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
        self.timeouts[connection] = connection.timeout
        self.connection_buffer[connection] = target
                    
    def run(self):
        if self.connection_buffer.keys():
            self.handle_connections()
        socket_name = socket.socket.__name__
        socket_objects = self.objects[socket_name]
        
        if socket_objects:
            self.number_of_sockets = number_of_sockets = len(socket_objects)            
            range_size = (number_of_sockets / 500) + 1
            for chunk in xrange(range_size):
                start_index = chunk * 500
                end_index = start_index + 500
                socket_list = socket_objects[start_index:end_index]
                self._handle_sockets(socket_list)            
            
        self.propagate()
        
    def _handle_sockets(self, socket_list):
        readable_sockets, writeable_sockets, errors = select.select(\
        socket_list, socket_list, [], 0.0)    
        
        if readable_sockets:
            self.handle_reads(readable_sockets)
 
        if writeable_sockets:
            self.handle_writes(writeable_sockets)
                                 
    def handle_connections(self):
        sockets = self.objects[socket.socket.__name__]
        for sock in self.connection_buffer.keys():            
            if sock in sockets:
                sockets.remove(sock)
            self.timeouts[sock] -= 1
            if not self.timeouts[sock]:
                del self.connection_buffer[sock]
                del self.timeouts[sock]
                if sock.timeout_notify:
                    sock.alert("{0} to {1} timed out after {2} frames".format(sock.instance_name, sock.target, sock.timeout), 0)
                self.add
                sock.delete()
                continue
            try: # this is how to do a non blocking connect
                sock.connect(self.connection_buffer[sock])
            except socket.error as error:
                if error.errno == CONNECTION_IN_PROGRESS: # waiting
                    continue
                elif error.errno == CONNECTION_IS_CONNECTED: # complete
                    self.add(sock)
                    if sock.on_connection:
                        sock.on_connection(sock, sock.getpeername())
                    del self.connection_buffer[sock]       
                        
    def handle_reads(self, readable_sockets):
        for sock in readable_sockets:
            try:
                getattr(sock, "handle_accept", sock.incoming)(sock)
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
        for sock in writable_sockets:
            sock.idle = False
            messages = self.write_buffer.get(sock)
            if messages:
                for index, message in enumerate(messages):
                    try:
                        sock.outgoing(sock, message)
                    except socket.error as error:
                        if error.errno == CONNECTION_WAS_ABORTED:           
                            self.alert("Failed to send {0} on {1}\n{2}",
                                      (self.write_buffer[sock], sock, error), 0)
                            sock.delete()
                        elif error.errno == 11: # EAGAIN on unix
                            self.alert("EAGAIN error when writing to {0}",
                                      (sock, ), 0)
                        else:
                            raise
                    else:
                        del self.write_buffer[sock][index]