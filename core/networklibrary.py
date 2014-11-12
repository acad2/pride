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

import defaults
import base
Event = base.Event

try:
    CONNECTION_IN_PROGRESS = errno.WSAEWOULDBLOCK
    CONNECTION_IS_CONNECTED = errno.WSAEISCONN
    CONNECTION_WAS_ABORTED = errno.WSAECONNABORTED
except:
    CONNECTION_IN_PROGRESS = errno.EINPROGRESS
    CONNECTION_IS_CONNECTED = errno.EISCONN
    CONNECTION_WAS_ABORTED = errno.ECONNABORTED
    
    
class Connection(base.Wrapper):
    
    defaults = defaults.Connection
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
    def __init__(self, sock=None, **kwargs):     
        if not sock:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        super(Connection, self).__init__(sock, **kwargs)
        sock.setblocking(0)
         
            
class Server(Connection):
    """usage: Event("Asynchronous_Network0", "create", "networklibrary.Server",
    incoming=myincoming, outgoing=myoutgoing, on_connection=myonconnection,
    name="My_Server", port=40010).post()"""
    
    defaults = defaults.Server
    
    def __init__(self, **kwargs):
        self.inbound_connection_options = {}
        super(Server, self).__init__(**kwargs)        
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, struct.pack('b', self.reuse_port))
        try:
            self.bind((self.interface, self.port))
        except socket.error:
            self.warning(traceback.format_exc() + "\nAddress already in use. Deleting %s\n" % self)
            return Event("Server", "delete", component=self).post()
        self.listen(self.backlog)        
        self.parent.servers.append(self)
        Event("Service_Listing0", "add_local_service", (self.interface, self.port), self.name).post()
        
        
class Outbound_Connection(Connection):
    
    defaults = defaults.Outbound_Connection
    
    def __init__(self, **kwargs):
        super(Outbound_Connection, self).__init__(**kwargs)    
        if not self.target:
            self.target = (self.ip, self.port)
        Event("Asynchronous_Network0", "buffer_connection", self, self.target).post()
       

class Download(Outbound_Connection):
    
    defaults = defaults.Download
    
    def __init__(self, **kwargs):
        self.received_chunks = []
        super(Download, self).__init__(**kwargs)
        if not self.filename:
            self.warning("Attempted to start a download without a filename to use")
            self.delete()
        try:
            self.file = open("%s_%s" % (self.filename_prefix, self.filename), "wb")       
        except IOError:
            filename = raw_input("Please provide a name for the downloaded file: ")
            self.file = open(filename, "wb")
        
    def on_connection(self, connection, address):
        self.thread = self._new_thread(connection)
        self.connection = connection
        network_chunk_size = self.network_chunk_size
        self.expecting = network_chunk_size + 17
        message = (str(0), str(network_chunk_size), self.filename)
        request = ":".join(message)
        Event("Asynchronous_Network0", "buffer_data", connection, request).post() 
        
    def outgoing(self, connection, data):
        print "sending request", data
        connection.send(data)
        
    def incoming(self, connection):
        try:
            next(self.thread)
        except StopIteration:
            print "Download complete!"
            try:
                assert self.filesize == self.total_file_size
            except AssertionError:
                print "WARNING: download did not receive expected amount of data"
                print "Expected: %s\tReceived: %s" % (self.total_file_size, self.filesize)
            else:
                print "Downloaded: %s (%s bytes in %i seconds)" % \
                (self.filename, self.filesize, time.time() - self.started_at)
            
            Event("download", "delete", component=self).post()
            if getattr(self, "exit_when_finished", None):
                sys.exit()

    def delete(self, *args):
        self.connection.close()
        self.file.close()
        super(Download, self).delete(*args)
                    
    def _new_thread(self, connection):
        network_chunk_size = self.network_chunk_size
        full_buffer = 17 + network_chunk_size
        size = connection.recv(16)
        self.total_file_size = int(size)
        print "Download of %s started. File size: %s" % (self.filename, self.total_file_size)
        self.started_at = time.time()
        yield
        while self.filesize < self.total_file_size:
            received = connection.recv(full_buffer)
            amount = len(received)
            self.expecting -= amount
            if self.expecting: # less then full amount received
                assert self.expecting == abs(self.expecting)
                if self.header_received: # already did the split and got file position
                    position = self.file.tell()
                    data = received # received is just data
                else: # have not gotten header yet
                    position, data = received.split(":", 1)
                    position = int(position)
                    self.header_received = True
                self.write_data(data, position)
            else: # received all the data expected
                position, data = received.split(":", 1)
                position = int(position)
                self.write_data(data, position)
                end = self.file.tell()
                self.filesize += end - position
                self.send_request(connection, end)
            yield
        Event("Asynchronous_Network0", "buffer_data", connection, "complete").post() 
        
    def send_request(self, connection, file_position):
        network_chunk_size = self.network_chunk_size
        file_size = self.total_file_size
        amount_left = file_size - file_position
        if amount_left < network_chunk_size:
            expecting = amount_left + 17
            request = ":".join((str(file_position), str(file_size), self.filename))
        else:
            expecting = network_chunk_size + 17
            request = ":".join((str(file_position), str(file_position + network_chunk_size), self.filename))
        self.expecting = expecting  
        Event("Asynchronous_Network0", "buffer_data", connection, request).post()      

    def write_data(self, data, position):
        self.file.seek(position)
        self.file.write(data)
        self.file.flush()
        
class Inbound_Connection(Connection):
    
    defaults = defaults.Inbound_Connection
    
    def __init__(self, sock, **kwargs):
        super(Inbound_Connection, self).__init__(sock, **kwargs)
        
 
class Upload(Inbound_Connection):
    
    defaults = defaults.Upload
    
    def __init__(self, sock, **kwargs):
        super(Upload, self).__init__(sock, **kwargs)
        self.settimeout(60)
        
    def outgoing(self, connection, data):
        connection.send(data)
        
    def incoming(self, connection): 
        try:
            start, end, filename = connection.recv(self.network_chunk_size).split(":", 2)
        except (socket.error, ValueError):
            #v: print "Finishing upload of %s" % self.filename
            self.file.close()
            self.close()
            self.delete()            
        #v: print "servicing request for %s: %s-%s" % (filename, start, end)
        start_index = int(start)
        end_index = int(end)
        if not self.file:
            self.load_file(filename)
            if self.file_size > mmap.ALLOCATIONGRANULARITY * 10:
                self.mmap_file = True
                Event("Asynchronous_Network0", "buffer_data", connection, str(self.file_size).zfill(16)).post()
        if self.mmap_file:
            data = self.read_from_memory(start_index)
        else:
            self.file.seek(start_index)
            data = self.file.read(end_index - start_index)    
        if not data:
            message = '0'
        else:
            message = start.zfill(16) + ":" + data
        Event("Asynchronous_Network0", "buffer_data", connection, message).post()
     
    def read_from_memory(self, start_index):
        chunk_size = mmap.ALLOCATIONGRANULARITY
        chunk_number, data_offset = divmod(start_index, chunk_size)        
        if self.file_size - start_index < self.network_chunk_size:
            chunk_number -= 1
            length = self.file_size - chunk_number * chunk_size
            data_offset = start_index - chunk_number * chunk_size
        else:
            length = self.network_chunk_size + data_offset
        chunk_offset = chunk_number * chunk_size
        arguments = (self.file.fileno(), length)
        options = {"access" : mmap.ACCESS_READ,
                   "offset" : chunk_offset}
        data_file = mmap.mmap(*arguments, **options)
        data_file.seek(data_offset)
        data = data_file.read(self.network_chunk_size)
        data_file.close()      
        return data
        
    def load_file(self, filename):
        self.filename = filename
        self.file_size = os.path.getsize(filename)
        self.file = open(filename, "rb")       
                 
        
class UDP_Socket(base.Wrapper):
            
    defaults = defaults.UDP_Socket
    
    def __init__(self, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        super(UDP_Socket, self).__init__(sock, **kwargs)
        self.bind((self.interface, self.port))
        self.settimeout(self.timeout)
        
        
class Asynchronous_Download(UDP_Socket):
            
    defaults = {}#Asynchronous_Download
    
    def __init__(self, **kwargs):
        super(Asynchronous_Download, self).__init__(**kwargs)
        for count, address in enumerate(self.file_seeders):
            message = (self.filename, str(count * self.network_chunk_size), 
                    str((count + 1) * self.network_chunk_size))
            request = ":".join(message)
            Event("Asynchronous_Network0", "buffer_data", self, request, address).post()    
    
    
class Multicast_Beacon(base.Wrapper):
    
    defaults = defaults.Multicast_Beacon
    
    def __init__(self, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        super(Multicast_Beacon, self).__init__(sock, **kwargs)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.packet_ttl)

        
class Multicast_Receiver(base.Wrapper):
    
    defaults = defaults.Multicast_Receiver
    
    def __init__(self, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        super(Multicast_Receiver, self).__init__(sock, **kwargs)
        #if self.reuseaddr:
        #    self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((self.listener_address, self.port))
        group_option = socket.inet_aton(self.multicast_group)
        multicast_configuration = struct.pack("4sL", group_option, socket.INADDR_ANY)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_configuration)
        # thanks to http://pymotw.com/2/socket/multicast.html for the above!
        
        
class Connection_File_Object(base.Base):
    
    def __init__(self, connection, **kwargs):
        super(Connection_File_Object, self).__init__(**kwargs)
        self.connection = connection
        
    def write(self, data):        
        Event("Asynchronous_Network0", "buffer_data", self.connection, data).post()
 
 
class Basic_Authentication_Client(base.Thread):
    
    defaults = defaults.Basic_Authentication_Client
    
    def __init__(self, **kwargs):
        super(Basic_Authentication_Client, self).__init__(**kwargs)
        self.thread = self._new_thread()
        
    def run(self):
        next(self.thread)
        
    def _new_thread(self):
        if self.parent.auto_login:
            username = self.parent.username
            password = self.parent.password
            print "automatically logging in as %s..." % username
        else:
            print "Please provide login information for", self
            username = raw_input("Username: ")
            password = hash(raw_input("Password: "))
        response = username+"\n"+str(password)
        Event("Asynchronous_Network0", "buffer_data", self.parent.connection, response).post()
        yield
        
        while not self.parent.network_buffer:
            yield        
        if self.parent.network_buffer in ("Invalid password", "Invalid username"):
            self.warning("%s supplied in login attempt" % self.network_buffer, "Shell")        
            self.login_stage = None
            self.network_buffer = None
            if "y" in raw_input("Retry?: ").lower():
                target = self.connection.getpeername()
                raise NotImplementedError
                Event("Asynchronous_Network0", "create", "networklibrary.Outbound_Connection",\
                target, incoming=self.incoming, outgoing=self.outgoing,\
                on_connection=self.on_connection).post()                
                #Event("Asynchronous_Network0", "disconnect", self.connection).post()
            else:
                self.warning("failed to login. Exiting...", self)
                Event("System0", "delete", self).post()
                raise NotImplementedError

                
class Basic_Authentication(base.Thread):
                    
    defaults = defaults.Basic_Authentication
    
    def __init__(self, connection, address, **kwargs):
        super(Basic_Authentication, self).__init__(**kwargs)
        self.thread = self._new_thread()
        self.connection = connection
        self.address = address
        
    def run(self):
        try:
            next(self.thread)
        except BaseException as exception:
            if type(exception) == AssertionError:
                response = "Invalid password"
            elif type(exception) == KeyError:
                response = "Invalid username"                
            elif isinstance(exception, StopIteration):
                raise                
            else:
                print "other exception occurred"
                raise
            
            Event("Asynchronous_Network0", "buffer_data", self.connection, response).post()        
            Event("Basic_Authentication", "delete", component=self).post()
            
    def _new_thread(self):
        while not self.parent.network_buffer[self.connection]:
            yield 
        username, password = [info for info in
                             self.parent.network_buffer[self.connection].strip().split("\n")]
        assert self.parent.authenticate[username] == hash(password)   
        self.parent.login_stage[self.address] = (username, "online")
            
                    
class Asynchronous_Network(base.Process):

    defaults = defaults.Asynchronous_Network
        
    def __init__(self, **kwargs):
        super(Asynchronous_Network, self).__init__(**kwargs)
        self.servers = []
        self.timeouts = {}
        self.write_buffer = {}
        self.connection_buffer = {}
        self.objects[socket.socket.__name__] = []
        self.readable_sockets = []
        self.writable_sockets = []
        Event("System0", "create", "networklibrary.Service_Listing", auto_start=False).post()
        
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
    
    def disconnect(self, connection):
        if self.write_buffer.has_key(connection):
            Event("Asynchronous_Network0", "disconnect", connection).post()
        else:
            connection.close()
            Event("Asynchronous_Network0", "delete", connection, component=self).post()
        
    def delete_server(self, server_name):
        for server in self.servers:
            if server.name == server_name:
                self.servers.remove(server)
                server.delete()
                
    def run(self):
        if self.connection_buffer.keys():
            #Event("Asynchronous_Network0", "handle_connections").post()          
            self.handle_connections()
        
        if self.objects[socket.socket.__name__]:
            number_of_socket_chunks = (len(self.objects[socket.socket.__name__])/500)
            for chunk in xrange(number_of_socket_chunks+1):
                socket_list = self.objects[socket.socket.__name__][chunk*500:(1+chunk)*500]
                readable_sockets, writeable_sockets, errors = select.select(\
                socket_list, socket_list, [], 0.0)    
 
                if readable_sockets:
                    self.handle_reads(readable_sockets)
                    #Event("Asynchronous_Network0", "handle_reads").post()
                if writeable_sockets:
                    self.handle_writes(writeable_sockets)
                    #Event("Asynchronous_Network0", "handle_writes").post()            
                
        if self in self.parent.objects[self.__class__.__name__]:
            Event("Asynchronous_Network0", "run").post()
                
    def handle_connections(self):
        sockets = self.objects[socket.socket.__name__]
        for sock in self.connection_buffer.keys():            
            if sock in sockets:
                sockets.remove(sock)
            self.timeouts[sock] -= 1
            if not self.timeouts[sock]:
                del self.connection_buffer[sock]
                sockets.append(sock)
                Event("Asynchronous_Network0", "delete", sock, component=self).post()
                sock.warning("Outbound Connection to %s timed out after %s frames" % (sock.target, sock.timeout))
                continue
            try: # this is how to properly do a non blocking connect
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
            if sock in self.servers:
                connection, address = sock.accept() # inbound connection received  
                options = sock.inbound_connection_options
                _connection = self.create(sock.inbound_connection_type, connection, **options)
                for method in ("on_connection", "incoming", "outgoing"):
                    if not getattr(_connection, method):
                        setattr(_connection, method, getattr(sock, method))
                
                if sock.on_connection: # server method to apply upon connection
                    sock.on_connection(_connection, address)
                
            else: # any encoding, and the actual sock.recv is done via sock.incoming
                try:
                    sock.incoming(sock)
                except socket.error as error:
                    if error.errno == CONNECTION_WAS_ABORTED:
                        sock.close()
                        sock.delete()
                    elif error.errno == 11: # EAGAIN on unix
                        self.warning("EAGAIN error reading %s" % sock)
                        
    def handle_writes(self, writable_sockets):
        for sock in writable_sockets:
            messages = self.write_buffer.get(sock)
            if messages:
                for index, message in enumerate(messages):
                    try:
                        sock.outgoing(sock, message)
                    except socket.error as error:
                        if error.errno == CONNECTION_WAS_ABORTED:
                            self.warning("Failed to send %s on %s" % (self.write_buffer[sock], sock), "%s" % error)
                            sock.delete()
                        elif error.errno == 11: # EAGAIN on unix
                            self.warning("EAGAIN error when writing to %s" % sock)
                    else:
                        del self.write_buffer[sock][index]
        
   
class Service_Listing(base.Process):
    
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
        
        for requester in messages:
            self.sendto(requester, "\n".join("Address: %s\tService: %s,%s" % (address, port, service_name)\
            for address, port, service_name in self.local_services.items()))