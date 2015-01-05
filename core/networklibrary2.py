import os
import mmap
import time
import socket

import base
import defaults
import networklibrary
Event = base.Event
            
            
class File_Service(vmlibrary.Process):

    defaults = defaults.File_Service
    
    def __init__(self, **kwargs):        
        super(File_Service, self).__init__(**kwargs)     
        options = {"interface" : self.interface,
                   "port" : self.port, 
                   "name" : self.instance_name, 
                   "inbound_connection_type" : "networklibrary2.Upload",
                   "share_methods" : tuple()}                           
        Event("Asynchronous_Network", "create", "networklibrary.Server", **options).post()    
    

"""class Tcp_Upload(networklibrary.Inbound_Connection):
                
    defaults = defaults.Tcp_Upload
    
    def __init__(self, **kwargs):
        super(Tcp_Upload, self).__init__(**kwargs)
        # this is a send only connection
        self.shutdown(socket.SHUT_RD)
        
    def on_connection(self, connection, address):
        with open(filename, "rb") as data_file:
            data = self.data = data_file.read()
            data_file.close()
            self.file_size = len(data)
        Event("Asynchronous_Network", "buffer_data", self, data[:self.network_packet_size]).post()
        
        if self.show_progress:
            latency = self.latency = Latency(name="send_file %s" % filename)
            self.frame_time = Average(size=100)
            self.upload_rate = Average(size=10)
            self.started_at = time.clock()        
        
    def outgoing(self, connection, data)
        sent = connection.send(data)
        self.file_size -= sent
        data = self.data = data[sent:]
        
        if self.show_progress:
            latency.update()
            upload_rate.add(amount_sent)
            frame_time.add(latency.latency)
            data_size = len(data)
            chunks_per_second = 1.0 / frame_time.average
            bytes_per_second = chunks_per_second * upload_rate.average
            time_remaining = (data_size / bytes_per_second)
            sys.stdout.write("\b"*80)
            sys.stdout.write("Upload rate: %iB/s. Time remaining: %i" % (bytes_per_second, time_remaining))
            
        if data:
            Event("Asynchronous_Network", "buffer_data", self, data[:self.network_packet_size]).post()
        else:
            Event(self.instance_name, "handle_close", component=self).post()
            
    def handle_close(self):        
        print "\n%s bytes uploaded in %s seconds" % (self.file_size, time.clock() - self.started_at)
        self.shutdown(socket.SHUT_WR)
        self.close()
        if getattr(self, "exit_when_finished", None):
            sys.exit()

            
class Tcp_Download(networklibrary.Outbound_Connection):
                
    def __init__(self, **kwargs):
        super(Tcp_Download, self).__init__(**kwargs)
        self.alert("{0} of {1} attempting connection...".format(self.instance_name, self.filename), 'v')
        
    def on_connection(self, connection, address):
        self.alert("{0} connected to {1}".format(self.instance_name, address), 1)
        self.file = open(self.filename, "wb")
        self.data_size = 0
        
        if self.show_progress:
            self.frame_time = Average(size=100)
            self.download_rate = Average(size=10)
            self.latency = Latency(name=self.instance_name)
            self.downloading = True
            self.started_at = time.clock()
        
        message = "{0} request for {1}".format(self.instance_name, self.filename)
        Event("Asynchronous_Network", "buffer_data", self, message).post()
        
    def incoming(self, connection):
        data = connection.recv(self.network_packet_size)
        if data == "upload of {0} complete".format(self.filename):
            return Event(self.instance_name, "handle_close", component=self).post()
            
        amount_received = len(data)
        self.download_rate.add(amount_received)
        self.data_size += amount_received
        _file = self.file
        _file.write(data)
        _file.flush()
        
        if self.show_progress:
            frame_time = self.frame_time
            latency = self.latency
            latency.update()            
            frame_time.add(latency.latency)
            chunks_per_second = 1.0 / frame_time.average
            bytes_per_second = chunks_per_second * download_rate.average
            sys.stdout.write("\b"*80)
            sys.stdout.write("Downloading at %iB/s" % bytes_per_second)
            sys.stdout.write("\b"*80)
                    
    def handle_close(self):        
        format_args = (filename, data_size, (time.clock() - started_at))
        self.alert("\nDownload of {0} complete ({1} bytes in {2} seconds)".format(*format_args)
        self.file.close()
        self.shutdown(socket.SHUT_RD)
        self.close()
        if getattr(self, "exit_when_finished", None):
            sys.exit()
"""           

            
class Upload(networklibrary.Inbound_Connection):
    
    defaults = defaults.Upload
    
    def __init__(self, **kwargs):
        super(Upload, self).__init__(**kwargs)
                
    def outgoing(self, connection, data):
        connection.send(data)
        
    def incoming(self, connection): 
        try:
            start, end, filename = connection.recv(self.network_packet_size).split(":", 2)
        except (socket.error, ValueError):
            self.alert("Finished upload of {0}".format(self.filename), "v")
            self.file.close()
            self.close()
            self.delete()
            return
        self.alert("servicing request for {0}: {1}-{2}".format(filename, start, end), "vvv")
        start_index = int(start)
        end_index = int(end)
        if not self.file:
            self.alert("Providing download of {0} for {1}".format(filename, connection.getpeername()), "v")
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

        
"""class Download(networklibrary.Outbound_Connection):
    
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
            self.alert("Attempted to start a download without a filename to use", 0)
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
        file = self.file
        file.seek(position)
        file.write(data)
        file.flush()
"""
  
class Multicast_Networker(networklibrary.Multicast_Beacon):
    
    defaults = defaults.Multicast_Networker
    
    def __init__(self, **kwargs):
        super(Multicast_Networker, self).__init__(**kwargs)
        
    def send_beacon(self, message, ip, port):
        Event("Asynchronous_Network", "buffer_data", self, message, (ip, port)).post()
        
    def create_listener(self, ip, port):
        self.create("networklibrary.Multicast_Receiver", ip=ip, port=port)
        
        
class Asynchronous_Download(networklibrary.UDP_Socket):
            
    defaults = {}#Asynchronous_Download
    
    def __init__(self, **kwargs):
        super(Asynchronous_Download, self).__init__(**kwargs)
        for count, address in enumerate(self.file_seeders):
            message = (self.filename, str(count * self.network_packet_size), 
                    str((count + 1) * self.network_packet_size))
            request = ":".join(message)
            Event("Asynchronous_Network", "buffer_data", self, request, address).post()    

            