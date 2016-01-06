import sys
import random
import hashlib

from pride import Instruction
import pride.security
import pride.decorators
from pride.security import hash_function, SecurityError
                    
class UnauthorizedError(SecurityError): pass
                    
@pride.decorators.required_arguments(no_args=True)
def remote_procedure_call(callback_name='', callback=None):
    def decorate(function):       
        call_name = function.__name__
        def _make_rpc(self, *args, **kwargs):  
            if callback_name:
                _callback = getattr(self, callback_name)
            else:
                _callback = callback or None
                
            instruction = Instruction(self.target_service, call_name, *args, **kwargs)
            if not (self.logged_in or self._logging_in) and call_name not in ("register", "login", "login_stage_two"):
                self.handle_not_logged_in(instruction, _callback)
            else:
                self.alert("Making request '{}.{}'", (self.target_service, call_name),
                        level=self.verbosity[call_name])            
                self.session.execute(instruction, _callback)
        return _make_rpc
    return decorate
      
def _split_byte(byte):
    """ Splits a byte into high and low order bytes. 
        Returns two integers between 0-15 """
    bits = format(byte, 'b').zfill(8)
    a, b = int(bits[:4], 2), int(bits[4:], 2)
    return a, b     
        
class Authentication_Table(object):
    """ Provides an additional factor of authentication. During account
        registration, the server generates an Authentication_Table for the
        newly registered client. The server records this table and sends a 
        copy to the client. When the client attempts to login, the server
        generates a random selection of indices and sends these to the client.
        The client is supposed to return the appropriate symbols from the
        table and the server matches what it expected against the response.
        
        Acts as "something you have", albeit in the form of data. """
    def __init__(self, rows=None, hash_function="sha256"):
        self.hash_function = hash_function
        size = 16
        if not rows:
            characters = [chr(x) for x in xrange(256)]
            rows = []
            for row_number in xrange(size):
                row = []
                while len(row) < size:
                    random_number = random._urandom(1)
                    try:
                        characters.remove(random_number)
                    except ValueError:
                        continue
                    else:
                        row.append(random_number)
                rows.append(''.join(row))
        self.rows = rows
    
    @staticmethod
    def generate_challenge(count=9):
        """ Generates count random pairs of indices, which range from 0-15 """
        return tuple(_split_byte(ord(byte)) for byte in random._urandom(count))
        
    def get_passcode(self, *args): 
        """ Returns a passcode generated from the symbols located at the 
            indices specified in the challenge"""
        return getattr(hashlib, 
                       self.hash_function)((''.join(self.rows[row][index] for 
                                            row, index in args))).digest()
    
    @staticmethod
    def compare(calculation, response):
        """ Compares two iterables in constant time """
        success = False
        for index, byte in enumerate(calculation):
            if response[index] != byte:
                break
        else:
            success = True
        return success
        
    def save(self, _file=None):
        """ Saves the table information to a bytestream. If _file is supplied,
            the bytestream is dumped to the file instead of returned.
            
            WARNING: This bytestream is a secret that authenticates a username
            and should be protected as any password or secure information. """
        text = ''.join(self.rows)
        if _file:
            _file.write(text)
            _file.flush()
        else:
            return text
    
    @classmethod
    def load(cls, text):
        """ Load a bytestream as returned by Authenticated_Table.save and 
            return an authenticated table object. """
        return cls(rows=[row for row in slide(text, 16)])

        
class Authenticated_Service(pride.base.Base):
   
    defaults = {# security related configuration options
                "hash_function" : "SHA256", "database_name" : '', "shared_key_size" : 32,
                "authentication_table_size" : 256, "challenge_size" : 9,
                
                # specific applications may wish to modify this
                "hkdf_table_update_info_string" : "Authentication Table Update",
                
                # non security related configuration options
                "database_type" : "pride.database.Database", 
                "validation_failure_string" :\
                   ".validate: Authorization Failure:\n   ip_blacklisted: {}" +
                   "    session_id logged in: {}\n    method_name: '{}'\n    " +
                   "login allowed: {}    registration allowed: {}",
                "allow_login" : True, "allow_registration" : True,
                "login_message" : "Welcome to the {}, {} from {}"}              
    
    verbosity = {"register" : 'vv', "login_stage_two" : 'vv', "validate_success" : 'vv',
                 "on_login" : 0, "login" : 'v', "authentication_success" : 'vv',
                 "authentication_failure" : 'v', "validate_failure" : "validate_failure",
                 "login_stage_two_hash_not_found" : "v"}
    
    flags = {"current_session" : ('', None)}
    
    database_structure = {"Users" : ("authentication_table_hash BLOB PRIMARY_KEY", 
                                     "authentication_table BLOB", "session_key BLOB",
                                     "username TEXT")}
                              
    database_flags = {"primary_key" : {"Users" : "authentication_table_hash"}}
    
    remotely_available_procedures = ("register", "login", "login_stage_two", "logout")
    
    rate_limit = {"login" : 2, "register" : 2}       
    
    mutable_defaults = {"_rate" : dict, "ip_whitelist" : list, "ip_blacklist" : list,
                        "_challenge_answer" : dict, "session_id" : dict}
                        
    inherited_attributes = {"database_structure" : dict, "database_flags" : dict,
                            "remotely_available_procedures" : tuple, "rate_limit" : dict}
    
    def __init__(self, **kwargs):
        super(Authenticated_Service, self).__init__(**kwargs)
        self._load_database()    
                
    def _load_database(self):
        if not self.database_name:
            _reference = '_'.join(name for name in self.reference.split("->") if name)
            name = self.database_name = "{}.db".format(_reference)
        else:
            name = self.database_name
        self.database = self.create(self.database_type, database_name=name,
                                    database_structure=self.database_structure,
                                    **self.database_flags)
            
    def register(self, username=''):
        self.alert("Registering new user", level=self.verbosity["register"])
        authentication_table = pride.security.random_bytes(self.authentication_table_size)
        hasher = hash_function(self.hash_function)
        hasher.update(authentication_table + ':' + "\x00" * self.shared_key_size)
        table_hash = hasher.finalize()
        self.database.insert_into("Users", (table_hash, authentication_table, 
                                            "\x00" * self.shared_key_size, username))
        return authentication_table
        
    def login(self, challenge):
        authentication_table_hash, ip = self.current_session
        client_challenge = Authentication_Table.generate_challenge(self.challenge_size)
        try:
            (saved_table,
            session_key) = self.database.query("Users", retrieve_fields=("authentication_table",
                                                                        "session_key"),
                                                where={"authentication_table_hash" : authentication_table_hash})
        except ValueError:
            response = pride.security.random_bytes(32)
        else:
            table = Authentication_Table.load(saved_table)
            response = table.get_passcode(*challenge)
            hasher = hash_function(self.hash_function)
            hasher.update(response + ':' + session_key)            
            
            correct_answer = table.get_passcode(*client_challenge)
            _answer_hasher = hash_function(self.hash_function)
            _answer_hasher.update(correct_answer + ':' + session_key)
            self._challenge_answer[authentication_table_hash] = _answer_hasher.finalize()
            self.alert("Issuing authentication challenge", level=self.verbosity["login"])
            response = hasher.finalize()
        return response, client_challenge
        
    def login_stage_two(self, hashed_answer, original_challenge):
        authentication_table_hash, ip = self.current_session           
        user_id = {"authentication_table_hash" : authentication_table_hash}
        self.alert("{} attempting to log in".format(ip),
                   level=self.verbosity["login_stage_two"])       
        
        # a fake key, iv, tag, and response for failed attempts
        encrypted_key = pride.security.random_bytes(self.shared_key_size + 48 + 32)
        try:
            (saved_table,
             session_key,
             username) = self.database.query("Users", 
                                             retrieve_fields=("authentication_table",
                                                              "session_key", "username"),
                                             where=user_id)
        except TypeError:
            self.alert("Failed to find authentication_table_hash in database for login_stage_two",
                       level=self.verbosity["login_stage_two_hash_not_found"])             
        else:         
            if (authentication_table_hash not in self.session_id and
                Authentication_Table.compare(self._challenge_answer[authentication_table_hash], hashed_answer)):
                del self._challenge_answer[authentication_table_hash]
                self.alert("Authentication success: {} '{}'",
                           (ip, username), level=self.verbosity["authentication_success"])
                self.session_id[authentication_table_hash] = username
                login_message = self.on_login()
                new_key = pride.security.random_bytes(self.shared_key_size)
                login_packet = pride.utilities.pack_data(new_key, login_message)                                                    
                encrypted_key = pride.security.encrypt(login_packet, session_key)
                
                hkdf = invoke("pride.security.hkdf_expand", self.hash_function,
                              length=self.authentication_table_size,
                              info=self.hkdf_table_update_info_string) 
                new_table = hkdf.derive(saved_table + ':' + new_key)
                table_hasher = hash_function(self.hash_function)
                table_hasher.update(new_table + ':' + new_key)
                new_table_hash = table_hasher.finalize()      
                self.database.update_table("Users", where=user_id, 
                                           arguments={"authentication_table_hash" : new_table_hash,
                                                       "authentication_table" : new_table,
                                                       "session_key" : new_key})
                self.session_id[new_table_hash] = username or new_table_hash                
            else:
                self.alert("Authentication Failure: {} '{}'",
                           (ip, username), 
                           level=self.verbosity["authentication_failure"])
        return encrypted_key
        
    def on_login(self):
        session_id, ip = self.current_session
        return self.login_message.format(self.reference, self.session_id[session_id], ip)
    
    def logout(self):
        authentication_table_hash, ip = self.current_session
        del self.session_id[authentication_table_hash]        
        
    def validate(self, session_id, peername, method_name):
        """ Determines whether or not the peer with the supplied
            session id is allowed to call the requested method.

            Sets current_session attribute to (session_id, peername) if validation
            is successful. """
        if (method_name not in self.remotely_available_procedures or
            peername[0] in self.ip_blacklist or 
            (session_id == '0' and method_name != "register") or
            (session_id not in self.session_id and method_name not in ("register", "login", "login_stage_two"))):
            
            self.alert(self.validation_failure_string,
                      (peername[0] in self.ip_blacklist, session_id in self.session_id,
                       method_name, self.allow_login, self.allow_registration),
                       level=self.verbosity["validate_failure"])
            return False         
       # if self.rate_limit and method_name in self.rate_limit:
       #     _new_connection = False
       #     try:
       #         self._rate[session_id][method_name].mark()
       #     except KeyError:
       #         latency = pride.datastructures.Latency("{}_{}".format(session_id, method_name))
       #         try:
       #             self._rate[session_id][method_name] = latency
       #         except KeyError:
       #             self._rate[session_id] = {method_name : latency}   
       #             _new_connection = True
       #     if not _new_connection:
       #         current_rate = self._rate[session_id][method_name].last_measurement                
       #         if current_rate < self.rate_limit[method_name]:
       #             self.alert("Rate of {} calls exceeded 1/{}s ({}); Denying request",
       #                     (method_name, self.rate_limit[method_name], current_rate),                           
       #                     level=self.verbosity["validate_failure"])
       #             return False        
        self.alert("Authorizing: {} for {}", 
                  (peername, method_name), 
                  level=self.verbosity["validate_success"])
        return True        
                        
    def __getstate__(self):
        state = super(Authenticated_Service, self).__getstate__()
        del state["database"]
        return state
        
    def on_load(self, attributes):
        super(Authenticated_Service, self).on_load(attributes)
        self._load_database()
        
        
class Authenticated_Client(pride.base.Base):   
    
    verbosity = {"register" : 0, "login" : 'v', "answer_challenge" : 'vv',
                 "login_stage_two" : 'vv', "register_sucess" : 0,
                 "auto_login" : 'v', "logout" : 'v', "login_message" : 0,
                 "delayed_request_sent" : "vv", "login_failed_already_logged_in" : 0}
                 
    defaults = {# security related configuration options
                "hash_function" : "SHA256", "authentication_table_size" : 256,
                "shared_key_size" : 32, "challenge_size" : 9,
                
                # note: while token file type may be changed to an alternative
                # file object, that file object must support the 'encrypted' flag
                # being passed to its constructor, and __enter__ and __exit__
                # token files are encrypted by default and non indexable,
                # meaning only a hash of the filename is stored
                "token_file_type" : "pride.fileio.Database_File",
                "token_file_encrypted" : True, "token_file_indexable" : False,
                
                # these may be passed explicitly when required
                "authentication_table_file" : '', "history_file" : '',
                
                # application specific needs may configure this when necessary
                "hkdf_table_update_info_string" : "Authentication Table Update",
                
                # non security related options
                "target_service" : "->Python->Authenticated_Service",
                "username_prompt" : "{}: Please provide the user name for {}@{}: ",
                "password_prompt" : "{}: Please provide the pass phrase or word for {}@{}: ",
                "ip" : "localhost", "port" : 40022, "auto_login" : True, 

                # a callback function may be passed to the constructor to handle
                # successful registration without defining/extending a class
                # this is convenient sometimes; otherwise forget about it
                 "_register_results" : None}
    
    mutable_defaults = {"_delayed_requests" : list}
    flags = {"_registering" : False, "logged_in" : False, "_logging_in" : False}
    
    def _get_host_info(self):
        return (self.ip, self.port)
    def _set_host_info(self, value):
        self.ip, self.port = value
    host_info = property(_get_host_info, _set_host_info)
    
    def _get_password(self):
        return (self._password or getpass.getpass(self.password_prompt))
    def _set_password(self, value):
        self._password = value
    password = property(_get_password, _set_password)    
    
    def _get_username(self):
        if not self._username:
            self._username = raw_input(self.username_prompt.format(self.reference,
                                                                   self.target_service,
                                                                   self.ip))
        return self._username
    def _set_username(self, value):        
        self._username = value
    username = property(_get_username, _set_username)
                
    def __init__(self, **kwargs):
        super(Authenticated_Client, self).__init__(**kwargs)
        self.password_prompt = self.password_prompt.format(self.reference, self.ip, self.target_service)
        self.session = self.create("pride.rpc.Session", '0', self.host_info)
        module = self.__module__
        name = '_'.join((self.username, module, type(self).__name__)).replace('.', '_')
        self.authentication_table_file = self.authentication_table_file or "{}_auth_table.key".format(name)
        self.history_file = self.history_file or "{}_history.key".format(name)
                                       
        if self.auto_login:
            self.alert("Auto logging in", level=self.verbosity["auto_login"])
            self.login()
    
    def _supply_username(self):
        self._registering = True
        return (self, self.username), {}
    @pride.decorators.with_arguments_from(_supply_username)
    @remote_procedure_call(callback_name="_store_auth_table")
    def register(self): pass
    
    def _store_auth_table(self, new_table):
        with self.create(self.token_file_type, self.authentication_table_file, 
                         'wb', encrypted=self.token_file_encrypted,
                         indexable=self.token_file_indexable) as _file:
            _file.write(new_table + ("\x00" * self.shared_key_size))
        self.alert("Registered successfully", level=self.verbosity["register_sucess"])  
        self._registering = False
        if self.auto_login:
            self.login()
        else:
            if self._register_results:
                self._register_results()
                
    def _hash_auth_table(self, auth_table, shared_key):
        hasher = hash_function(self.hash_function)
        hasher.update(auth_table + ':' + shared_key)
        return hasher.finalize()
        
    def _token_not_registered(self): # called when login fails because user is not registered
        if not self._registering:
            self.alert("Login token for '{}' not found", (self.username, ), level=0)
            if pride.shell.get_permission("Register now? "):                    
                self.register()
                
    def _get_auth_table_hash(self):        
        with self.create(self.token_file_type, self.authentication_table_file, 
                         'rb', encrypted=self.token_file_encrypted,
                         indexable=self.token_file_indexable) as _file:
            auth_table = self.auth_table = _file.read(self.authentication_table_size)
            shared_key = self.shared_key = _file.read(self.shared_key_size)                  
        self._logging_in = True    
        self.session.id = self._hash_auth_table(auth_table, shared_key)
        challenge = Authentication_Table.generate_challenge(self.challenge_size)
        table = Authentication_Table.load(auth_table)
        hasher = hash_function(self.hash_function)
        hasher.update(table.get_passcode(*challenge) + ':' + shared_key)
        self._answer = hasher.finalize()        
        return (self, challenge), {}
            
    @pride.decorators.on_exception(IOError, _token_not_registered)
    @pride.decorators.with_arguments_from(_get_auth_table_hash)
    @remote_procedure_call(callback_name="login_stage_two")
    def login(self): pass
    
    def _answer_challenge(self, response):
        hashed_answer, challenge = response
        if hashed_answer != self._answer:
            raise SecurityError("Server responded with incorrect response to challenge")

        answer = Authentication_Table.load(self.auth_table).get_passcode(*challenge)
        hasher = hash_function(self.hash_function)
        hasher.update(answer + ':' + self.shared_key)
        self.alert("Answering challenge", level=self.verbosity["answer_challenge"])
        return (self, hasher.finalize(), challenge), {}
        
    @pride.decorators.with_arguments_from(_answer_challenge)
    @remote_procedure_call(callback_name="decrypt_new_secret")
    def login_stage_two(self, authenticated_table_hash, answer, challenge): pass
    
    def decrypt_new_secret(self, encrypted_key):
        with self.create(self.token_file_type, self.authentication_table_file, 
                         'r+b', encrypted=self.token_file_encrypted,
                         indexable=self.token_file_indexable) as _file:
            auth_table = _file.read(self.authentication_table_size)
            shared_key = _file.read(self.shared_key_size)
            try:
                packed_key_and_message = pride.security.decrypt(encrypted_key, shared_key)
            except ValueError:
                self.alert("Login attempt failed; Already logged in.", 
                           level=self.verbosity["login_failed_already_logged_in"])
            else:
                new_key, login_message = pride.utilities.unpack_data(packed_key_and_message, 2)
                self.shared_key = new_key
                hkdf = invoke("pride.security.hkdf_expand", self.hash_function,
                                    length=self.authentication_table_size,
                                    info=self.hkdf_table_update_info_string) 
                                    
                new_table = hkdf.derive(auth_table + ':' + new_key)            
                _file.truncate(0)
                _file.seek(0)
                _file.write(new_table)
                _file.write(new_key)     
                _file.flush()
                self.session.id = self._hash_auth_table(new_table, new_key)
                self.on_login(login_message)
        
    def on_login(self, login_message):
        self.logged_in = True
        self._logging_in = False
        self.alert("{}", [login_message], level=self.verbosity["login_message"])
        for instruction, callback in self._delayed_requests:
            self.alert("Making delayed request: {}",
                      [(instruction.component_name, instruction.method)],
                      level=self.verbosity["delayed_request_sent"])
            self.session.execute(instruction, callback)
            
    def _reset_login_flags(self):
        self.logged_in = False
        self.session.id = '0'
        
    @pride.decorators.call_if(logged_in=True)
    @pride.decorators.exit(_reset_login_flags)
    @remote_procedure_call(callback=None)
    def logout(self): 
        """ Logout self.username from the target service. If the user is logged in,
            the logged_in flag will be set to False and the session.id set to '0'.
            If the user is not logged in, this is a no-op. """
    
    def handle_not_logged_in(self, instruction, callback):
        self.alert("Not logged in")        
        if self.auto_login or pride.shell.get_permission("Login now? :"):
            self._delayed_requests.append((instruction, callback))
            self.login()            
                
    def delete(self):
        if self.logged_in:
            self.logout()
        super(Authenticated_Client, self).delete()
        
        
class Authenticated_Peer(Authenticated_Service):
    
    defaults = {"authenticated_client_type" : "pride.authentication2.Authenticated_Client",
                "peer_ip" : "localhost", "peer_port" : 40022, "username" : '',
                "target_service" : ''}
                            
    remotely_available_procedures = ("test_method", )
        
  #  def __init__(self, **kwargs):
  #      super(Authenticated_Peer, self).__init__(**kwargs)
  #      self.create(self.authenticated_client_type, ip=self.peer_ip, port=self.peer_port,
  #                  username=self.username, target_service=self.target_service)
        
    def on_login(self):
        session_id, peername = self.current_session
        client_config = self.client_configuration
        client_config["ip"] = peername[0]
        self.create(self.authenticated_client_type, **client_config)
        
    def test_method(self, *args):
        self.alert("Test method has been called {}".format(args), level=0)
        
def test_Authenticated_Service2():
    service = objects["->Python"].create(Authenticated_Service)
    client = objects["->Python"].create(Authenticated_Client, auto_login=False)
    client.register()
    Instruction(client.reference, "login").execute(priority=2.5)
    
if __name__ == "__main__":
    peer = objects["->Python"].create(Authenticated_Peer, target_service="->Python->Peer1")
    peer1 = objects["->Python"].create(Authenticated_Peer, target_service="->Python->Peer")
    client = peer.create(Authenticated_Client, target_service="->Python->Peer1", auto_login=False)
    client.register()
    #peer1.current_session = ("localhost", 40022)
    #peer1.on_login()
    #peer1.current_session = None