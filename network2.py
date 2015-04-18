import os
import collections
import hmac
import getpass
import hashlib
import sqlite3
import binascii
import functools

import mpre
import mpre.base as base
import mpre.defaults as defaults
import mpre.network as network
import mpre.fileio as fileio
from mpre.utilities import Latency, timer_function
Instruction = mpre.Instruction
           
def Authenticated(function):
    def call(instance, sender, packet):
        if sender in instance.logged_in:
            response = function(instance, sender, packet)
        else:
            response = "login_result 0"
        return response
    return call
    
    
class Network_Service(network.Udp_Socket):
    
    defaults = defaults.Network_Service
    
    end_request_errors = {"0" : "Invalid Request"}
    
    def __init__(self, **kwargs):
        super(Network_Service, self).__init__(**kwargs)
        self.expecting_response = collections.deque(maxlen=20)
        self.received = collections.deque(maxlen=20)
        self.packet_cache = collections.deque(maxlen=20)
        self._return_to = {}
        self.sent_at = {}
        self.resent = set()

    def socket_recv(self):
        packet, sender = self.recvfrom(self.network_packet_size)

        # (hopefully) reliable udp mechanisms
        id, response_to, data = packet.split(" ", 2)     
        self.received.append(response_to)
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
                    return
        
        # packet parsing
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
                if not end_of_request: # malformed request
                    response = self.invalid_request(sender, packet)
                    self.send_data(response, sender, response_to, False)  
                    return

        if end_of_request:
            self.alert("Request finished {}",
                       [request],
                       'vv')
            return
            
        self.alert("handling response {} {}",
                   [command, value[:32]],
                   level='vv')
        #print "reaction: ", self.instance_name, command, value[:45]
        response = getattr(self, command)(sender, value)
        response = response if response else "end_request"
        expect_response = response[:11] != "end_request"
        
        self.alert("Sending response: {} in response to {}",
                   [response, id],
                   level='vvv')
        self.send_data(response, sender, response_to, expect_response)
        
        #self._handle_resends()
        
    def send_data(self, data, to=None, 
                  response_to='None', expect_response=True):
        reaction = ''
        lowercase_data = data.lower()
        
        if lowercase_data[:6] == "return":
            flag, reaction, data = data.split(" ", 2)
        
        id, packet = self._make_packet(response_to, data)
        
        if reaction:
            self._return_to[id] = reaction
            
        if to[0] == "localhost":
            to = ("127.0.0.1", to[1])                            
        
        self.sendto(packet, to)
        
        if expect_response:
            self.expecting_response.append((to, id))
            
        self.packet_cache.append((id, packet))
        self.sent_at[id] = timer_function()
        self.alert("sent packet {} {} to {} in response to {}",
                   [id, data[:32], to, response_to],
                   level='vv')                               
        
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
                        
                self.parallel_method("Network", "send", 
                                self,
                                packet,
                                target)
                self.resent.add((target, id))               
               
    def invalid_request(self, sender, packet):
        self.alert("Invalid reaction request\nFrom:{}\nPacket:{}",
                   [sender, packet],
                   level=0)
                                    
        return "end_request invalid_request " + packet
    
    def _make_packet(self, response_to, data):
        message = response_to + " " + data
        id = str(hash(message))
        return id, id + " " + message
        
    def demo_reaction(self, sender, packet):
        print "im a demo reaction for", sender, packet
        counter = int(packet)
        if counter >= 1000:
            print "1000 reactions happened between {} and {}".format(self, sender)
            response = ''
        else:
            response = "demo_reaction " + str(counter + 1)
        return response
        
        
class Authenticated_Service(base.Reactor):
    
    defaults = defaults.Authenticated_Service
                
    def __init__(self, **kwargs):
        super(Authenticated_Service, self).__init__(**kwargs)
        self.invalid_attempts = {}
        self.logged_in = {}
        
        db = self.database = sqlite3.connect(self.database_filename)
        db.text_factory = str
                    
        cursor = db.cursor()
        
        cursor.execute("CREATE TABLE IF NOT EXISTS Credentials(" + 
                       "email TEXT, username TEXT, password TEXT" +
                       ", address TEXT)")
                       
        self._add_user = '''INSERT INTO Credentials VALUES(?, ?, ?, ?)'''
        self._remove_user = "DELETE FROM Credentials WHERE username=:username"
        self._select_user = """SELECT username, password FROM Credentials WHERE username = ?"""
            
    def _sql_encrypt(self, password, salt=None):
        salt = os.urandom(64) if not salt else salt
        iterations = self.hash_rounds
        digest = salt + password
        hash_functions = dict((name, getattr(hashlib, name)) for name in 
                               hashlib.algorithms if name != "pbkdf2_hmac")         
        while iterations > 0:
            for hash_function in hashlib.algorithms:
                digest = hash_functions[hash_function](digest).digest()
                iterations -= 1
        return salt + digest
        
    def __getstate__(self):
        state = super(Authenticated_Service, self).__getstate__()
        del state["database"]
        return state
        
    def on_load(self, attributes):
        super(Authenticated_Service, self).on_load(attributes)
        self.database = sqlite3.connect(self.database_filename)
        
    def login(self, sender, packet):
        username, password = packet.split(" ", 1)
        
        if username in self.logged_in.values():
            return 'login_result failed 1'
            
        database = self.database#sqlite3.connect(self.database_filename)
        cursor = database.cursor()
        
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
            if (hmac.compare_digest(hashed, correct_password) if 
                hasattr(hmac, "compare_digest") else 
                hashed == correct_password):
                     
                self.logged_in[sender] = username
                response = "success " + self.login_message
            else:
                invalid_attempts = self.invalid_attempts
                
                attempts = invalid_attempts.get(sender, 0)
                invalid_attempts.setdefault(sender, attempts + 1)
                response = "failed 0"            
                
        return "login_result " + response
        
    def register(self, sender, packet):
        database = self.database#sqlite3.connect(self.database_filename)
        cursor = database.cursor()
        
        email, username, password = packet.split(" ", 2)

        self.alert("Registering new user {} {} {}",
                   [email, username, sender],
                   level='v')
       
        try:
            cursor.execute(self._add_user, (email, username,
                                            self._sql_encrypt(password), str(sender)))
            
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
        return "register_results " + response

    def logout(self, sender, packet):
        if sender in self.logged_in:            
            del self.logged_in[sender]
    
    @Authenticated
    def modify_user(self, sender, packet):
        mode, user = packet.split(" ", 1)
        database = sqlite3.connect(self.database_filename)
        cursor = database.cursor()
        
        if mode == "remove":
            cursor.execute(self._remove_user, 
                          {"Username" : self.logged_in[sender]})
            database.commit()
            del self.logged_in[user]

      
class Authenticated_Client(base.Reactor):
            
    defaults = defaults.Authenticated_Client
    
    login_errors = {"0" : "Invalid username or password",
                    "1" : "Already logged in"}
                    
    def __init__(self, **kwargs):
        super(Authenticated_Client, self).__init__(**kwargs)        
        self.logged_in = False
        self.reaction(self.target, self.login())        
        
    def login(self, sender=None, packet=None):
        self.alert("Attempting to login", level=0)#'v')
        
        username = (self.username if self.username else 
                    raw_input("Please provide username for {}: ".format(
                               self.instance_name)))
                    
        password = self.password if self.password else getpass.getpass()
        return "login {} {}".format(username, password)
                
    def register(self, sender, packet):        
        self.alert(packet, 
                  (self.email, self.username, "*" * len(self.password)),
                   level=0)
        
        email = (self.email if self.email else 
                 raw_input("Please register an email address: "))
        while ' ' in email:
            self.alert("Invalid email address. Cannot contain spaces",
                       level=0)
            email = (self.email if self.email else 
                     raw_input("Please register an email address: "))
                 
        username = (self.username if self.username else 
                    raw_input("Please register a username: "))
                    
        password = self.password if self.password else getpass.getpass()        
        
        return "register {} {} {}".format(email, username, password)
    
    def register_results(self, sender, packet):
        if "success" in packet:
            return self.login(sender, packet)
        else:
            self.alert("Error encountered when attempting to register with {}\n{}",
                       [sender, packet])
        
    def login_result(self, sender, packet):
        if "success" in packet:
            self.alert(packet, level=0)
            self.logged_in = True
        elif "register" in packet:
            flag, message = packet.split(" ", 1)
            return self.register(sender, message)
        else:
            failed, code = packet.split(" ", 1)
            error = self.login_errors[code]
            self.alert("Login failed; {}", [error], level=0)
        
        
class Service_Listing(Network_Service):
    defaults = defaults.Network_Service.copy()
    
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
            
           
class File_Service(base.Reactor):
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
                  
  
class Download(base.Reactor):
    
    defaults = defaults.Download
    
    def __init__(self, **kwargs):
        super(Download, self).__init__(**kwargs)
        self.data_remaining = 0
        
        filename = self.filename
        self.file = open("{}_{}".format(self.filename_prefix, filename), 'wb')    
                
        self.reaction(self.target, "get_filesize " + filename)                  
                
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
                       [self.filename, self.target])        
        
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
        
        
class Tcp_Client_Proxy(network.Tcp_Client):
    
    def recv(self):
        print self.instance_name, "receiving data!"
        request = self.socket.recv(self.network_packet_size)        
        service_name, command, value = request.split(" ", 2)
        self.respond_with("reply")
        request = command + " " + value
        self.reaction(service_name, request)
              
    def reply(self, sender, packet):
        self.send_data(str(sender) + " " + packet)

                           
class Tcp_Service_Test(network.Tcp_Client):
    
    def on_connect(self):        
        self.send_data("Interpreter_Service login username password")
                           
    def recv(self):
        self.network_buffer += self.recv(self.network_packet_size)
        print "got results!: ", self.network_buffer
        
def test_proxy():
    verbosity = 'vvv'
    options = {"verbosity" : verbosity,
               "port" : 40000}
               
    options2 = {"verbosity" : verbosity,
                "target" : ("localhost", 40000)}
                
    Instruction("Metapython", "create", "network2.Tcp_Service_Proxy", **options).execute()
    Instruction("Metapython", "create", "network2.Tcp_Service_Test", **options2).execute()
    
def test_reliability():
    Instruction("Metapython", "create", Network_Service, port=4000, verbosity='vvv').execute()
    Instruction("Metapython", "create", Network_Service, port=4001, verbosity='vvv').execute()
    Instruction("Network_Service1", "send_data", "demo_reaction 0", to=("localhost", 4000)).execute()

    
if __name__ == "__main__":
    from mpre.tests.network2 import test_file_service, test_authentication
    test_reliability()
   # test_authentication()
   # test_file_service()
   # test_proxy()