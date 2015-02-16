import os
import collections
import hmac
import getpass
import hashlib
import sqlite3
import binascii
import functools

import mpre.base as base
import mpre.defaults as defaults
import mpre.network as network
import mpre.fileio as fileio
from mpre.utilities import Latency, timer_function
Instruction = base.Instruction
           
def Authenticated(function):
    def call(instance, sender, packet):
        if sender in instance.logged_in:
            response = function(instance, sender, packet)
        else:
            response = "login_result 0"
        return response
    return call
    
    
"""class Authenticated(object):
    
    def __init__(self, function):
        self.function = function
      #  functools.update_wrapper(self, function)
        
    def __call__(self, instance, sender, packet):
        if sender in instance.logged_in:
            response = self.function(sender, packet)
        else:
            response = "login_result 0"
        return response
"""
        
class Service(network.Udp_Socket):
    
    defaults = defaults.Service
    
    end_request_errors = {"0" : "Invalid Request"}
    
    def __init__(self, **kwargs):
        super(Service, self).__init__(**kwargs)
        self.expecting_response = collections.deque(maxlen=20)
        self.received = collections.deque(maxlen=20)
        self.packet_cache = collections.deque(maxlen=20)
        self._return_to = {}
        self.sent_at = {}
        self.resent = set()

    def socket_recv(self):
        data, address = self.recvfrom(self.network_packet_size + 128)
        try:
            self.network_buffer[address].append(data)
        except KeyError:
            self.network_buffer[address] = [data]
                        
        base.Parallel_Instructions.append(self.instance_name)
        
    def react(self):
        received = self.received
        for sender, packet in self.read_messages():
            if sender in base.Component_Resolve.keys():
                local = True
            else:
                local = False
                
            id, response_to, data = packet.split(" ", 2)     
            received.append(response_to)
            request = (sender, response_to)
            
            self.alert("Checking to see if {} is expected",
                       [request],
                       level='vv')    
            try:                   
                self.expecting_response.remove(request)
            except ValueError:
                if response_to == "None":
                    self.alert("Received a new connection {}",
                               [id],
                               'vv')
                else:
                    self.alert("Received duplicate packet {}",
                               [id],
                               level='vv')
                    if request in self.resent:
                        self.resent.remove(request)  
                    else:
                        continue
            
            end_of_request = False
            if response_to in self._return_to:
                command = self._return_to[response_to]
                value = data
                if value[:11] == "end_request":
                    value = value[11:]
                    end_of_request = True
            else:
                if data[:11] == "end_request":
                    data = data[12:]
                    end_of_request = True
                try:
                    command, value = data.split(" ", 1)
                except ValueError:
                    continue
                                       
            self.alert("handling response {} {}",
                       [command, value[:32]],
                       level='vv')
            #print "reaction: ", self.instance_name, command, value[:45]
            response = getattr(self, command)(sender, value)
            
            if end_of_request:
                self.alert("Request finished {}",
                           [request],
                           'vv')
                continue
            else:
                response = response if response else "end_request"
                expect_response = response[:11] != "end_request"
                
                self.alert("Sending response: {} in response to {}",
                           [response, id],
                           level='vvv')
                self.rpc(sender, response, id, expect_response, local)
        
        self._handle_resends()
        
    def rpc(self, target, data, 
               response_to="None", expect_response=True,
               local=False):            
        if not local:
            reaction = ''
            lowercase_data = data.lower()
            
            if lowercase_data[:6] == "return":
                flag, reaction, data = data.split(" ", 2)
            
            id, packet = self.make_packet(response_to, data)
            
            if reaction:
                self._return_to[id] = reaction
                
            if target[0] == "localhost":
                target = ("127.0.0.1", target[1])                            
            
            self.public_method("Asynchronous_Network", "buffer_data", 
                               self,
                               packet,
                               target)
            
            if expect_response:
                self.expecting_response.append((target, id))
                
            self.packet_cache.append((id, packet))
            self.sent_at[id] = timer_function()
            self.alert("sent packet {} {} to {} in response to {}",
                       [id, data[:32], target, response_to],
                       level='vv')                       
            
        else:
            assert False
            super(Service, self).rpc(target, data, response_to)
        
    def _handle_resends(self):
        packet_cache = dict((id, packet) for id, packet in self.packet_cache)
        sent_at = self.sent_at
        resend_after = .2
        
        for target, id in self.expecting_response:
            if timer_function() - sent_at[id] > resend_after:
                packet = packet_cache[id]
                
                self.alert("Resending {}",
                           [id],
                           level=0)
                        
                self.public_method("Asynchronous_Network", "buffer_data", 
                                self,
                                packet,
                                target)
                self.resent.add((target, id))        
        
    def read_messages(self):
        messages = super(Service, self).read_messages()
        for address, packets in self.network_buffer.items():
            for packet in packets:
                messages.append((address, packet))
            self.network_buffer[address] = []
        
        return messages            
     
    def make_packet(self, response_to, data):
        message = response_to + " " + data
        id = str(hash(message))
        return id, id + " " + message
               
    def invalid_request(self, sender, packet):
        self.alert("Invalid rpc request\nFrom:{}\nPacket:{}",
                   [sender, packet],
                   level=0)
                                    
        return "end_request invalid_request " + packet
        
        
class Authenticated_Service(Service):
    
    defaults = defaults.Authenticated_Service
                
    def __init__(self, **kwargs):
        super(Authenticated_Service, self).__init__(**kwargs)
        self.invalid_attempts = {}
        self.logged_in = {}
        
        db = self.database = sqlite3.connect("metapython.db")#self.database_filename)
        db.text_factory = str
                    
        db.create_function("encrypt", 1, self._sql_encrypt)
        cursor = self.cursor = db.cursor()
        
        cursor.execute("CREATE TABLE IF NOT EXISTS Credentials(" + 
                       "email TEXT, username TEXT, password TEXT" +
                       ", address TEXT)")
                       
        self._add_user = '''INSERT INTO Credentials VALUES(?, ?, encrypt(?), ?)'''
        self._remove_user = "DELETE FROM Credentials WHERE username=:username"
        self._select_user = """SELECT username, password FROM Credentials WHERE username = ?"""

    def _sql_encrypt(self, password, salt=None):
        salt = os.urandom(64) if not salt else salt
        encrypted = hashlib.pbkdf2_hmac('sha512', 
                                        password.encode('utf-8'), 
                                        salt, 
                                        100000)
        assert len(encrypted) == 64
        return salt + encrypted
            
    def login(self, sender, packet):
        username, password = packet.split(" ", 1)
        
        if username in self.logged_in.values():
            return 'login_result failed 1'
            
        database = self.database
        cursor = self.cursor
        
        self.alert("{} attempting to login from {}",
                   [username, sender],
                   level='v')                   
        
        cursor.execute(self._select_user, [username])       
        database.commit()            
        try:
            username, correct_password = cursor.fetchone()
        except TypeError as error:
            response = "register "
            message = ("Please register username before logging in\n" +
                       "Registration requires:" + "\n\temail: {}" + 
                       "\n\tusername: {}" + "\n\tpassword: {}")
            response += message
            database.rollback()            
        else:
            hashed = self._sql_encrypt(password, correct_password[:64])
                        
            if not hmac.compare_digest(hashed, correct_password):
                invalid_attempts = self.invalid_attempts
                
                attempts = invalid_attempts.get(sender, 0)
                invalid_attempts.setdefault(sender, attempts + 1)
                response = "failed 0"

            else:
                self.logged_in[sender] = username
                response = "success " + self.login_message
                
        return "login_result " + response
        
    def register(self, sender, packet):
        database = self.database
        cursor = self.cursor
        
        email, username, password = packet.split(" ", 2)

        self.alert("Registering new user {} {} {}",
                   [email, username, sender],
                   level='v')
       
        try:
            cursor.execute(self._add_user, (email, username,
                                            password, str(sender)))
            
        except sqlite3.Error as error:            
            self.alert("Database error: {}",
                       [error],
                       0)
            database.rollback()
            response = 'failed'
        else:
            database.commit()
            response = "success"
            
            self.alert("{} {} {} registered successfully",
                       [username, email, sender],
                       level='vv')
        return response

    def logout(self, sender, packet):
        if sender in self.logged_in:            
            del self.logged_in[sender]
    
    @Authenticated
    def modify_user(self, sender, packet):
        mode, user = packet.split(" ", 1)
        
        if mode == "remove":
            self.cursor.execute(self._remove_user, {"Username" : username})
            self.database.commit()
            del self.logged_in[user]

      
class Authenticated_Client(Service):
            
    defaults = defaults.Authenticated_Client
    
    login_errors = {"0" : "Invalid username or password",
                    "1" : "Already logged in"}
                    
    def __init__(self, **kwargs):
        super(Authenticated_Client, self).__init__(**kwargs)
        target = self.target
        self.rpc(target, self.login(None, None))
        self.logged_in = False
        
    def login(self, sender, packet):
        self.alert("Attempting to login", level='v')
        
        username = (self.username if self.username else 
                    raw_input("Please provide username for {}: ".format(
                               self.instance_name)))
                    
        password = self.password if self.password else getpass.getpass()
        return "login {} {}".format(username, password)
                
    def register(self, sender, packet):        
        print packet.format(self.email, self.username, "*" * len(self.password))
        
        email = (self.email if self.email else 
                 raw_input("Please register an email address: "))
                 
        username = (self.username if self.username else 
                    raw_input("Please register a username: "))
                    
        password = self.password if self.password else getpass.getpass()        
        
        return "return login register {} {} {}".format(email, username, password)
        
    def login_result(self, sender, packet):
        if "success" in packet:
            self.alert(packet, level=0)
            self.logged_in = True
        elif "register" in packet:
            return self.register(sender, packet)
        else:
            failed, code = packet.split(" ", 1)
            error = self.login_errors[code]
            self.alert("Login failed; {}", [error], level=0)
        
        
class Service_Listing(Service):
    defaults = defaults.Service.copy()
    
    def __init__(self, **kwargs):
        self.services = {}
        super(Service_Listing, self).__init__(**kwargs)
        
    def set_service(self, sender, packet):
        service_name, address = packet.split(" ", 1)                
        self.services[address] = service_name
        return "set success"
        
    def remove_service(self, sender, packet):
        service_name, address = packet.split(" ", 1)
        del self.services[address]
        
    def send_listing(self, sender, packet):
        return "\n".join("Address: {: >20} Service: {: > 5}".format\
                        (address, service_info) for  address, service_info\
                        in self.services.items())
            
           
class File_Service(Service):
    defaults = defaults.File_Service
    
    def __init__(self, **kwargs):
        super(File_Service, self).__init__(**kwargs)
                
    def slice_request(self, sender, slice_info):
        filename, file_position, request_size = slice_info.split()
        seek_index = int(file_position)
        request_size = int(request_size)
        
        if request_size >= self.mmap_threshold:
            _file, offset = fileio.Mmap(filename, seek_index)
            data = _file[offset:offset + request_size]            
        
        else:
            _file = open(filename, 'rb')
            _file.seek(seek_index)
            data = _file.read(request_size)
            _file.close()
            
        self.alert("retrieved {}/{} bytes of data/requested", 
                   [len(data), request_size],
                   level='vv')
        return "record_data " + file_position + " " + data        
        
    def get_filesize(self, sender, filename):
        try:
            response = str(os.path.getsize(filename))
        except WindowsError:
            response = "0"
        return "set_filesize " + response
                  
  
class Download(Service):
    
    defaults = defaults.Download
    
    def __init__(self, **kwargs):
        super(Download, self).__init__(**kwargs)
        self.data_remaining = 0
        
        filename = self.filename
        self.file = open("{}_{}".format(self.filename_prefix, filename), 'wb')    
                
        self.rpc(self.target, "get_filesize " + filename)                  
                
    def make_request(self):
        if self.bytes_remaining > 0:
            file_position = self.file.tell()
            request_size = min(self.bytes_remaining, self.network_packet_size)
            request = "{} {} {} {}".format("slice_request",
                                            self.filename, 
                                            file_position, 
                                            request_size)
        else:
            request = ""
            self.alert("finished downloading, sending close request" + "*"*40, level=0)
            self.file.close()
        return request
                
    def set_filesize(self, sender, value):
        filesize = int(value)
        if filesize:
            self.bytes_remaining = filesize
            return self.make_request()            
        else:
            self.alert("File {} was not available for download from {}",
                       [filename, self.target])        
        
    def record_data(self, sender, data):
        file_position, file_data = data.split(" ", 1)
        seek_position = int(file_position)
        
        file = self.file
        file.seek(seek_position)        
        file.write(data)
        file.flush()
        self.bytes_remaining -= file.tell() - seek_position
        return self.make_request()
        
        
class Tcp_Service_Proxy(network.Server):

    def __init__(self, **kwargs):
        super(Tcp_Service_Proxy, self).__init__(**kwargs)
        self.inbound_connection_type = Tcp_Client_Proxy
                    
    def on_connect(self, connection):
        pass
        
        
class Tcp_Client_Proxy(network.Inbound_Connection):
    
    def socket_recv(self):
        request = self.recv(self.network_packet_size)        
        service_name, command, value = request.split(" ", 2)
        
        request = "return reply " + command + " " + value
        self.rpc(service_name, request)
              
    def reply(self, sender, packet):
        self.public_method("Asynchronous_Network", "buffer_data",
                           self, str(sender) + " " + packet)

                           
class Tcp_Service_Test(network.Outbound_Connection):
    
    def on_connect(self):        
        self.public_method("Asynchronous_Network", "buffer_data",
                           self, "Interpreter_Service login username password")
                           
    def socket_recv(self):
        self.network_buffer += self.recv(self.network_packet_size)
        print "got results!: ", self.network_buffer
        
def test_proxy():
    verbosity = 'vvv'
    options = {"verbosity" : verbosity,
               "port" : 40000}
               
    options2 = {"verbosity" : verbosity,
                "target" : ("localhost", 40000)}
                
    Instruction("System", "create", "network2.Tcp_Service_Proxy", **options).execute()
    Instruction("System", "create", "network2.Tcp_Service_Test", **options2).execute()
    
    
if __name__ == "__main__":
    from mpre.tests.network2 import test_file_service, test_authentication
   # test_authentication()
   # test_file_service()
   # test_proxy()