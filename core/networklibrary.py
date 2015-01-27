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
    def _get_protocol(self):
        return (self.on_connect, self.socket_recv, self.socket_send)

    def _set_protocol(self, protocol):
        on_connect, socket_recv, socket_send = protocol
        self.on_connect = on_connect
        self.socket_recv = socket_recv
        self.socket_send = socket_send
    protocol = property(_get_protocol, _set_protocol)

    on_connect = None
    socket_recv = None
    socket_send = None

    def _get_address(self):
        return (self.ip, self.port)
    address = property(_get_address)

    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket())
        super(Socket, self).__init__(**kwargs)
        self.setblocking(self.blocking)
        self.settimeout(self.timeout)

        #if self.timeout_after:
         #   instruction = self.idle_instruction = Instruction(self.instance_name, "handle_idle")
          #  instruction.priority = self.timeout_after
           # instruction.execute()

    def delete(self):
        self.close()
        Instruction("Asynchronous_Network", "debuffer_data", self).execute()
        Instruction("Asynchronous_Network", "remove_socket", self).execute()
        super(Socket, self).delete()

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

    def on_connect(self, connection):
        Instruction("Asynchronous_Network", "add", connection).execute()


class Server(Connection):
    """usage: Instruction("Asynchronous_Network", "create", "networklibrary.Server",
    socket_recv=mysocket_recv, socket_send=mysocket_send, on_connect=myonconnection,
    name="My_Server", port=40010).execute()"""

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
            Instruction("Asynchronous_Network", "add_service", (self.interface, self.port), self.name).execute()

    def socket_recv(self, server):
        _socket, address = server.accept() # inbound connection received

        connection = self.create(server.inbound_connection_type,
                                  wrapped_object=_socket,
                                  peer_address=address,
                                  **server.client_options)

        # Asynchronous_Network.add happens in on_connect
        server.on_connect(connection)

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

        Instruction("Connection_Manager", "buffer", self).execute()
                
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
                    self.on_connect(self)

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
        instruction = self.wait_instruction = Instruction(self.instance_name, "wait")

    def run(self):
        try:
            next(self.thread)
        except StopIteration:
            self.delete()

    def wait(self):
        self.alert("\t{0} waiting for reply", [self.instance_name], level="vvv")
        #self.wait_instruction.execute()

    def _new_thread(self):
        connection = self.connection
        
        if self.auto_login:
            username, password = self.credentials
            self.alert("Attempting to automatically log in as {0}...",
                       (username, ), "v")
        else:
            username = raw_input("Please provide credentials for {0}\nUsername: "\
                                 .format(self.instance_name))
            password = getpass.getpass()

        password = hash(password) # WARNING: not seriously secure!
        response = username+"\n"+str(password)

        Instruction("Asynchronous_Network", "buffer_data", connection, response).execute()
        self.wait()
        yield

        while not self.network_buffer[connection]:
            self.wait()
            yield

        reply = self.network_buffer[connection].lower()
        if reply in ("invalid password", "invalid username"):
            self.alert("{0} supplied in login attempt",
                      (reply, ), 0)
            if reply == "invalid password":
                self.handle_invalid_password()
            else:
                self.handle_invalid_username()
        else:
            self.handle_success(connection)

    def retry(self):
        if "y" in raw_input("Retry?: ").lower():
            target = self.connection.getpeername()
            Instruction("Asynchronous_Network", "create", "networklibrary.Outbound_Connection",
                        target, socket_recv=self.socket_recv, socket_send=self.socket_send,\
                        on_connect=self.on_connect).execute()
            #Instruction("Asynchronous_Network", "disconnect", self.connection).execute()
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

    def __init__(self, **kwargs):
        super(Basic_Authentication, self).__init__(**kwargs)
        self.thread = self._new_thread()        
        
    def run(self):
        try:
            next(self.thread)
        except (AssertionError, KeyError, StopIteration) as exception:
            switch = {AssertionError : self.handle_invalid_password,
                      KeyError : self.handle_invalid_username,
                      StopIteration : self.handle_success}
            switch[type(exception)](self.connection)
            self.connection = None
            self.delete()

    def _new_thread(self):
        connection = self.connection
        while not self.network_buffer[connection]:
            self.alert("{0} waiting for reply", [self.instance_name], level="vvv")
            yield
        self.alert("credentials received", level="vv")
        username, password = self.network_buffer.pop(connection).strip().split("\n", 1)
        connection.username = username
        assert self.authenticate[username] == int(password)
        self.network_buffer[connection] = ''
        
    def handle_invalid_username(self, connection):
        Instruction("Asynchronous_Network", "buffer_data", connection, self.invalid_username_string).execute()

    def handle_invalid_password(self, connection):
        Instruction("Asynchronous_Network", "buffer_data", self.connection, self.invalid_password_string).execute()

    def handle_success(self, connection):
        Instruction(self.parent, "log_in", connection).execute()

    def delete(self):
        self.connection = None
        super(Basic_Authentication, self).delete()


class Connection_Manager(vmlibrary.Thread):

    defaults = defaults.Thread.copy()

    def __init__(self, **kwargs):
        self._buffer = []
        super(Connection_Manager, self).__init__(**kwargs)
        self.thread = self._new_thread()
       # self.running = False

    def buffer(self, connection):
        self._buffer.append(connection)

    def debuffer(self, connection):
        self._buffer.remove(connection)
        
    def run(self):
        return next(self.thread)

    def _new_thread(self):
        buffer = self._buffer
        while True:
        
            new_buffer = []
            while buffer:
                connection = buffer.pop()
                if not connection.deleted and not connection.attempt_connection():
                    new_buffer.append(connection)
                    
            buffer = self._buffer = new_buffer
            yield
           


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

        self.services = {}
        self.write_buffer = {}

        super(Asynchronous_Network, self).__init__(**kwargs)
        self.objects[socket.socket.__name__] = []
        self.create("networklibrary.Service_Listing")
        self.connection_manager = self.create(Connection_Manager)

        instruction = self.update_instruction = Instruction("Asynchronous_Network", "_update_range_size")
        instruction.priority = self.update_priority
        instruction.execute()

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

    """def remove(self, connection):
        self.debuffer_data(connection)
        super(Asynchronous_Network, self).remove(connection)
        print "removing", connection
        import gc
        for item in gc.get_referrers(connection):
            print
            print item"""

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

    def remove_socket(self, sock):
        try:
            self.remove(sock)
        except:
            self.alert("{0} was removed but was not in {1}",
                       [sock.instance_name, self.instance_name],
                       level='v')

    def _update_range_size(self):
        self._socket_range_size = range((len(self.objects[self._socket_name]) / 500) + 1)
        self.update_instruction.execute()

    def run(self):
        self.run_instruction.execute()
        self.connection_manager.run()

        sockets = self.objects[self._socket_name]
        for chunk in self._socket_range_size:
            # select has a max # of file descriptors it can handle, which
            # is about 500 (at least on windows).We can avoid this limitation
            # by sliding through the socket list in slices of 500 at a time
            socket_list = sockets[self._slice_mapping[chunk]]

            readable, writable, errors = self._select(socket_list, socket_list, [], 0.0)
            if readable:
                self.handle_reads(readable)
            if writable:
                self.handle_writes(writable)

    def handle_errors(self, socket_list):
        self.alert("Encountered sockets with errors", level=0)

    def handle_reads(self, readable_sockets):
        for sock in readable_sockets:
            try:
                sock.socket_recv(sock)
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
            messages = self.write_buffer.get(sock)
            if messages:
                sock.idle = False
                for index, message in enumerate(messages):
                    try:
                        sock.socket_send(sock, message)
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
                    else:
                        del self.write_buffer[sock][index]


class Service_Listing(vmlibrary.Process):

    defaults = defaults.Service_Listing

    def __init__(self, **kwargs):
        super(Service_Listing, self).__init__(**kwargs)
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
        self.services[address] = (port, service)

    def remove_local_service(self, address):
        del self.local_services[address]

    def remove_service(self, address):
        del self.services[address]

    def run(self):
        print "List of known network services: "
        for address, service_name in self.services.items():
            print "Address: %s\tService Name: %s" % (address, service_name)

    def process_request(self):
        for requester in self.read_messages():
            listings = "\n".join("Address: %s\tService: %s" % (address, service_info) for address, service_info in self.local_services.items())
            self.send_to(requester, listings)
