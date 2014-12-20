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
    def __init__(self, **kwargs):     
        connection_info = defaults.Connection
        socket_family = connection_info["socket_family"]
        socket_type = connection_info["socket_type"]
        kwargs.setdefault("wrapped_object", socket.socket(socket_family, socket_type))
        super(Connection, self).__init__(**kwargs)
        self.setblocking(0)
         
    def delete(self):
        self.close()
        super(Connection, self).delete()
        
        
class Server(Connection):
    """usage: Event("Asynchronous_Network", "create", "networklibrary.Server",
    incoming=myincoming, outgoing=myoutgoing, on_connection=myonconnection,
    name="My_Server", port=40010).post()"""
    
    defaults = defaults.Server
    
    def __init__(self, **kwargs):
        self.inbound_connection_options = {}
        super(Server, self).__init__(**kwargs)        
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, self.reuse_port)
        try:
            self.bind((self.interface, self.port))
        except socket.error:
            message = traceback.format_exc() + "\nAddress already in use. Deleting %s\n" % self
            self.alert(message, 5)
            return Event("Server", "delete", component=self).post()
        self.listen(self.backlog)   
        self.parent.servers.append(self)
        Event("Service_Listing", "add_local_service", (self.interface, self.port), self.name).post()
        
        
class Outbound_Connection(Connection):
    
    defaults = defaults.Outbound_Connection
    
    def __init__(self, **kwargs):
        super(Outbound_Connection, self).__init__(**kwargs)    
        if not self.target:
            self.target = (self.ip, self.port)
        Event("Asynchronous_Network", "buffer_connection", self, self.target).post()
       

class Download(Outbound_Connection):
    
    defaults = defaults.Download
    
    def __init__(self, **kwargs):
        self.received_chunks = []
        super(Download, self).__init__(**kwargs)
        
    def on_connection(self, connection, address):
        self.thread = self._new_thread(connection)
        self.connection = connection
        network_packet_size = self.network_packet_size
        self.expecting = network_packet_size + 17
        self.header_received = False
        if not self.filename:
            self.alert("Attempted to start a download without a filename to use", 4)
            self.delete()
        else:
            try:
                self.file = open("%s_%s" % (self.filename_prefix, self.filename), "wb")       
            except IOError:
                filename = raw_input("Please provide a name for the downloaded file: ")
                self.file = open(filename, "wb")
        message = (str(0), str(network_packet_size), self.filename)
        request = ":".join(message)        
        Event("Asynchronous_Network", "buffer_data", connection, request).post() 
        
    def outgoing(self, connection, data):
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

    def delete(self):
        try:
            self.file.close()
        except AttributeError:
            pass
        super(Download, self).delete()
        if getattr(self, "exit_when_finished", None):
            sys.exit()
                    
    def _new_thread(self, connection):
        network_packet_size = self.network_packet_size
        full_buffer = 17 + network_packet_size
        size = connection.recv(16)
        self.total_file_size = int(size)
        print "Download of %s started. File size: %s" % (self.filename, self.total_file_size)
        self.started_at = time.time()
        yield
        while self.filesize < self.total_file_size:
            received = connection.recv(full_buffer)
            amount = len(received)
            self.expecting -= amount
            assert self.expecting == abs(self.expecting)
            if not self.header_received: # beginning of request
                self.header_received = True
                position, data = received.split(":", 1)
                position = int(position)
            else: # did not receive all the data
                data = received
                position = self.file.tell()
            self.write_data(data, position)
            if not self.expecting: # received all the data expected
                end = self.file.tell()
                self.filesize += end - position
                self.send_request(connection, end)
            yield
        Event("Asynchronous_Network", "buffer_data", connection, "complete").post() 
        
    def send_request(self, connection, file_position):
        network_packet_size = self.network_packet_size
        file_size = self.total_file_size
        amount_left = file_size - file_position
        if amount_left < network_packet_size:
            expecting = amount_left + 17
            request = ":".join((str(file_position), str(file_size), self.filename))
        else:
            expecting = network_packet_size + 17
            request = ":".join((str(file_position), str(file_position + network_packet_size), self.filename))
        self.expecting = expecting
        self.header_received = False
        Event("Asynchronous_Network", "buffer_data", connection, request).post()      

    def write_data(self, data, position):
        self.file.seek(position)
        self.file.write(data)
        self.file.flush()
        
        
class Inbound_Connection(Connection):
    
    defaults = defaults.Inbound_Connection
    
    def __init__(self, **kwargs):
        super(Inbound_Connection, self).__init__(**kwargs)
                
 
class Upload(Inbound_Connection):
    
    defaults = defaults.Upload
    
    def __init__(self, **kwargs):
        super(Upload, self).__init__(**kwargs)
        self.settimeout(60)
        
    def outgoing(self, connection, data):
        connection.send(data)
        
    def incoming(self, connection): 
        try:
            start, end, filename = connection.recv(self.network_packet_size).split(":", 2)
        except (socket.error, ValueError):
            self.alert("Finished upload of {0}".format(self.filename), 1)
            self.file.close()
            self.close()
            self.delete()
            return
        self.alert("servicing request for {0}: {1}-{2}".format(filename, start, end), 1)
        start_index = int(start)
        end_index = int(end)
        if not self.file:
            self.alert("Providing download of {0} for {1}".format(filename, connection.getpeername()), 3)
            self.load_file(filename)
            if self.file_size > mmap.ALLOCATIONGRANULARITY * 10:
                self.mmap_file = True    
            file_size = str(self.file_size).zfill(16)
            Event("Asynchronous_Network", "buffer_data", connection, str(self.file_size).zfill(16)).post()
        if self.mmap_file:
            data = self.read_from_memory(start_index)
        else:
            self.file.seek(start_index)
            data = self.file.read(end_index - start_index)    
        if not data:
            message = '0'
        else:
            message = start.zfill(16) + ":" + data
        Event("Asynchronous_Network", "buffer_data", connection, message).post()
     
    def read_from_memory(self, start_index):
        chunk_size = mmap.ALLOCATIONGRANULARITY
        chunk_number, data_offset = divmod(start_index, chunk_size)        
        if self.file_size - start_index < self.network_packet_size:
            chunk_number -= 1
            length = self.file_size - chunk_number * chunk_size
            data_offset = start_index - chunk_number * chunk_size
        else:
            length = self.network_packet_size + data_offset
        chunk_offset = chunk_number * chunk_size
        arguments = (self.file.fileno(), length)
        options = {"access" : mmap.ACCESS_READ,
                   "offset" : chunk_offset}
        data_file = mmap.mmap(*arguments, **options)
        data_file.seek(data_offset)
        data = data_file.read(self.network_packet_size)
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
            message = (self.filename, str(count * self.network_packet_size), 
                    str((count + 1) * self.network_packet_size))
            request = ":".join(message)
            Event("Asynchronous_Network", "buffer_data", self, request, address).post()    
    
    
class Multicast_Beacon(base.Wrapper):
    
    defaults = defaults.Multicast_Beacon
    
    def __init__(self, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        super(Multicast_Beacon, self).__init__(sock, **kwargs)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.packet_ttl)

        
class Multicast_Receiver(base.Wrapper):
    
    defaults = defaults.Multicast_Receiver
    
    def __init__(self, **kwargs):
        kwargs["wrapped_object"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        super(Multicast_Receiver, self).__init__(**kwargs)

        # thanks to http://pymotw.com/2/socket/multicast.html for the below
        self.bind((self.listener_address, self.port))
        group_option = socket.inet_aton(self.multicast_group)
        multicast_configuration = struct.pack("4sL", group_option, socket.INADDR_ANY)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_configuration)
        
     
class Basic_Authentication_Client(base.Thread):
    
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
        self.alert("Waiting for reply", 5)
        
    def _new_thread(self):
        if self.auto_login:
            username, password = self.credentials
            self.alert("automatically logging in as {0}...".format(username), 3)          
        else:
            print "Please provide login information for", self
            username = raw_input("Username: ")
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
            self.alert("{0} supplied in login attempt".format(reply), 4)        
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
            self.alert("failed to login. Exiting...", 5)
                        
    def handle_invalid_username(self):
        self.retry()
        
    def handle_invalid_password(self):
        self.retry()
    
    def handle_success(self, connection):
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
            self.alert("waiting for reply", 0)
            yield 
        self.alert("credentials received", 0)
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
        Event("System", "create", "networklibrary.Service_Listing", auto_start=False).post()
            
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
            Event("Asynchronous_Network", "disconnect", connection).post()
        else:
            connection.close()
            Event("Asynchronous_Network", "delete", connection, component=self).post()
     
    def delete_server(self, server_name):
        for server in self.servers:
            if server.name == server_name:
                self.servers.remove(server)
                server.delete()
                
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
                    sock.alert("{0} to {1} timed out after {2} frames".format(sock.instance_name, sock.target, sock.timeout), 4)
                self.add
                sock.delete()
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
                options["wrapped_object"] = connection
                for method in ("on_connection", "incoming", "outgoing"):
                    options.setdefault(method, getattr(sock, method))     
                
                _connection = self.create(sock.inbound_connection_type, **options)
                
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
                        self.alert("EAGAIN error reading %s" % sock, 4)
                    else:
                        raise
                        
    def handle_writes(self, writable_sockets):
        for sock in writable_sockets:
            messages = self.write_buffer.get(sock)
            if messages:
                for index, message in enumerate(messages):
                    try:
                        sock.outgoing(sock, message)
                    except socket.error as error:
                        if error.errno == CONNECTION_WAS_ABORTED:
                            message = "Failed to send %s on %s" % (self.write_buffer[sock], sock) + "%s" % error
                            self.alert(message, 4)
                            sock.delete()
                        elif error.errno == 11: # EAGAIN on unix
                            self.alert("EAGAIN error when writing to %s" % sock, 4)
                        else:
                            raise
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
    
    def process_request(self):
        for requester in self.read_messages():            
            listings = "\n".join("Address: %s\tService: %s" % (address, service_info) for address, service_info in self.local_services.items())
            self.send_to(requester, listings)
            
            
class File_Server(base.Base):

    defaults = defaults.File_Server
    
    def __init__(self, **kwargs):
        super(File_Server, self).__init__(**kwargs)     
        
        if self.asynchronous_server:
            options = {"interface" : self.interface,
                       "port" : self.port, 
                       "name" : "File_Server", 
                       "inbound_connection_type" : "networklibrary.Upload"}                           
            Event("Asynchronous_Network", "create", "networklibrary.Server", **options).post()    

    def send_file(self, filename='', ip='', port=40021, show_progress=True):
        to = (ip, port)
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender.connect(to)
        with open(filename, "rb") as data_file:
            data = data_file.read()
            data_file.close()
        file_size = len(data)
        latency = Latency(name="send_file %s" % filename)
        frame_time = Average(size=100)
        upload_rate = Average(size=10)
        started_at = time.clock()
        latency.update()
        while data:
            amount_sent = sender.send(data[:self.network_packet_size])            
            data = data[self.network_packet_size:]
            if show_progress:
                latency.update()
                upload_rate.add(amount_sent)
                frame_time.add(latency.latency)
                data_size = len(data)
                chunks_per_second = 1.0 / frame_time.average
                bytes_per_second = chunks_per_second * upload_rate.average
                time_remaining = (data_size / bytes_per_second)
                sys.stdout.write("\b"*80)
                sys.stdout.write("Upload rate: %iB/s. Time remaining: %i" % (bytes_per_second, time_remaining))
        print "\n%s bytes uploaded in %s seconds" % (file_size, time.clock() - started_at)
        sender.close()
        if getattr(self, "exit_when_finished", None):
            sys.exit()

    def receive_file(self, filename='', interface="0.0.0.0", port=40021, show_progress=True):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((interface, port))
        server.listen(1)        
        _file = open(filename, "wb")
        frame_time = Average(size=100)
        download_rate = Average(size=10)
        latency = Latency(name="receive_file %s" % filename)
        downloading = True
        started_at = time.clock()
        data_size = 0
        print "Waiting for connection...", interface, port
        receiver, _from = server.accept()
        print "Connection received"
        receiver.settimeout(2)
        while downloading:
            latency.update()
            data = receiver.recv(self.network_packet_size)
            if not data:
                downloading = False
            amount_received = len(data)
            download_rate.add(amount_received)
            data_size += amount_received
            receiver.settimeout(2)
            _file.write(data)
            _file.flush()
            if show_progress:
                frame_time.add(latency.latency)
                chunks_per_second = 1.0 / frame_time.average
                bytes_per_second = chunks_per_second * download_rate.average
                sys.stdout.write("\b"*80)
                sys.stdout.write("Downloading at %iB/s" % bytes_per_second)
        sys.stdout.write("\b"*80)
        print "\nDownload of %s complete (%s bytes in %s seconds)" % \
        (filename, data_size, (time.clock() - started_at - 2.0))
        _file.close()
        receiver.close()
        server.close()
        if getattr(self, "exit_when_finished", None):
            sys.exit()
            