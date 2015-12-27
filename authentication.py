import hashlib
import random
import hkdf
import sqlite3
import getpass

import pride
import pride.errors
import pride.base
import pride.database
import pride.utilities
import pride.shell
Instruction = pride.Instruction
objects = pride.objects

class UnauthorizedError(Warning): pass         
                 
def derive_key_from_password(salt, password=None, hash_name="sha512", iterations=50000,
                             prompt="Please supply the password for the key: ",
                             dklen=None):
    return hashlib.pbkdf2(hash_name, getpass.getpass(prompt) if password is None else password, 
                          salt, iterations, dklen)
    
def derive_random_key(random_size=128, salt_size=32):
    bytes = random._urandom(random_size)
    salt = random._urandom(salt_size)
    return hkdf.extract(bytes, salt)
    
def derive_encryption_key(key, size=32, purpose="Encryption"):
    return hkdf.expand(key, size, purpose)
    
def derive_session_id(key, size=32, purpose='Session Identifier'):
    return hkdf.expand(key, size, purpose)

def derive_mac_key(key, size=32, purpose="Message Authentication Code"):
    return hkdf.expand(key, size, purpose)
    
def required_arguments(no_args=False, no_kwargs=False, requires_args=False, 
                       requires_kwargs=False, **_kwargs):
    def decorate(function):
        def new_call(*args, **kwargs):
            raise_error = False
            if ((no_args and args) or (requires_args and not args) or
                (no_kwargs and kwargs) or (requires_kwargs and kwargs)):
                raise pride.errors.ArgumentError("Unable to call {}".format(function))
            if _kwargs:
                for key, value in _kwargs.items():
                    if kwargs[key] != value:
                        raise pride.errors.ArgumentError("expected {} == {}; found {} == {}".format(key, value, key, kwargs[value]))
            return function(*args, **kwargs)
        return new_call
    return decorate
    
@required_arguments(no_args=True)
def remote_procedure_call(callback_name='', callback=None):
   # print "\nrpc callback info: ", callback_name, callback
    def decorate(function):
  #      print "Rpc decorating: ", function
       # if not (callback_name or callback):
       #     raise pride.errors.ArgumentError("callback_name or callback not supplied for {}".format(function))        
        call_name = function.__name__
        def _make_rpc(self, *args, **kwargs):       
            self.alert("Making request '{}.{}'", (self.target_service, call_name),
                       level=self.verbosity[call_name])
            self.session.execute(Instruction(self.target_service, call_name, 
                                             *args, **kwargs), 
                                             callback or 
                                             getattr(self, callback_name) if callback_name else None)
        return _make_rpc
    return decorate
  
def with_arguments(entry_function):
    def decorate(function):
        def new_call(*args, **kwargs):
            args, kwargs = entry_function(*args, **kwargs)
            return function(*args, **kwargs)
        return new_call
    return decorate

def enter(enter_function):
    def decorate(function):
        def new_call(*args, **kwargs):
            enter_function(*args, **kwargs)
            return function(*args, **kwargs)
        return new_call
    return decorate
    
def exit(exit_function):
    def decorate(function):
        def new_call(*args, **kwargs):
            result = function(*args, **kwargs)
            exit_function(*args, **kwargs)
            return result
        return new_call
    return decorate
    
def call_if(**conditions):
    def decorate(function):
        def new_call(self, *args, **kwargs):
            for key, value in conditions.items():
                if not getattr(self, key) == value:
                    break
            else:
                return function(self, *args, **kwargs)
        return new_call
    return decorate
    
def _split_byte(byte):
    """ Splits a byte into high and low order bytes. 
        Returns two integers between 0-15 """
    bits = format(byte, 'b').zfill(8)
    a, b = int(bits[:4], 2), int(bits[4:], 2)
    return a, b
    
def _x_bytes_at_a_time(string, x=16):
    """ Yields x bytes at a time from string """
    while string:
        yield string[:x]
        string = string[x:]
    
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
    def generate_challenge(count=6):
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
        return cls(rows=[row for row in _x_bytes_at_a_time(text)])

        
class Authenticated_Service(pride.base.Base):
    """ Provides functionality for user registration and login, and
        provides interface for use with blacklisted/whitelisted/authenticated
        decorators. Currently uses the secure remote password protocol
        for authentication. """
    defaults = {"allow_registration" : True, "allow_login" : True,
                "protocol_component" : "->Python->Secure_Remote_Password",
                "database_name" : '', "login_message" : '', 
                "login_fail_message" : "Invalid username or password",
                "current_session" : (None, None), "session_id_size" : 256,
                "validation_failure_string" : \
                   ".validate: Authorization Failure:\n    blacklisted: {}" +
                   "    session_id logged in: {}\n    method_name: '{}'\n    " +
                   "login allowed: {}    registration allowed: {}",
                "hkdf_table_update_string" : "updating the authentication table",
                "hash_function" : "sha512", "database_type" : "pride.database.Database"}
    
    parser_ignore = ("protocol_component", "current_sesion", "session_id_size")
    
    verbosity = {"validate_success" : "vvv", "validate_failure" : "vv",
                 "register_attempt" : "vv", "register_success" : "vv",
                 "login_attempt" : "vv", "multiple_login" : "vv",
                 "login_success" : "vv", "login_unregistered" : "vv",
                 "logout_failure" : "vv"}
   
    inherited_attributes = {"rate_limit" : dict, "remotely_available_procedures" : tuple,
                            "database_structure" : dict, "database_flags" : dict}
    
    rate_limit = {"login" : 2, "register" : 2}            
    
    remotely_available_procedures = ("register", "login", "login_stage_two", "logout")
    
    mutable_defaults = {"_rate" : dict, "_table_challenge" : dict, "ip_blacklist" : list,
                        "session_id" : dict} # session_id maps session id to username
        
    database_structure = {"Credentials" : ("username TEXT PRIMARY_KEY", "salt TEXT", 
                                           "verifier BLOB", "authentication_table BLOB",
                                           "history BLOB")}
    
    database_flags = {"text_factory" : str,
                      "primary_key" : {"Credentials" : "username"},
                      "return_cursor" : True}
            
    def __init__(self, **kwargs):
        self.ip_whitelist = ["127.0.0.1", "localhost"]        
        super(Authenticated_Service, self).__init__(**kwargs)
        self._load_database()
        
    def _load_database(self):
        if not self.database_name:
            _instance_name = '_'.join(name for name in self.instance_name.split("->") if name)
            name = self.database_name = "{}.db".format(_instance_name)
        else:
            name = self.database_name
        self.database = self.create(self.database_type, database_name=name,
                                    database_structure=self.database_structure,
                                    **self.database_flags)
        for table, structure in self.database_structure.items():
            self.database.create_table(table, structure)
                
    def register(self, username, password):
        """ Register a username and corresponding password. The
            authenticated_service.allow_registration flag must be True or
            registration will fail. If the username is already registered,
            registration will fail. Returns True on successful registration. """
        self.alert("Attempting to register " + username, 
                   level=self.verbosity["register_attempt"])
        if self.allow_registration:
            database = self.database
            try:
                database.query("Credentials", 
                               retrieve_fields=("salt", "verifier"), 
                               where={"username" : username})
            except sqlite3.OperationalError as error:
                database.alert("{} when querying Credentials table".format(error), level=0)
            else:
                cursor = database.cursor
                registered = cursor.fetchone()
                if not registered:       
                    salt, password_verifier = objects["->Python->Secure_Remote_Password"].new_verifier(username, password)
                    authentication_table = Authentication_Table().save()
                    try:
                        database.insert_into("Credentials", 
                                            (username, salt, 
                                             str(password_verifier), 
                                             authentication_table,
                                             "\x00" * 256))
                    except sqlite3.IntegrityError as error:
                        database.alert("sqlite3 IntegrityError registering {}: {}",
                                       (username, error), level=0)
                        database.rollback()
                    else:
                        database.commit()
                        self.alert("user {} registered successfully".format(username),
                                   level=self.verbosity["register_success"])
                        return authentication_table
         
    def login(self, username, credentials):
        """ Attempt to log in as username using credentials. The default
            implementation uses the secure remote password protocol, which is
            a 2 stage protocol. Login success and failure are not determined
            until login_stage_2 returns. 
            
            Alternative single stage login protocols may be implemented by
            overloading this method. Note that implementing a traditional
            password hashing authentication system is arguably less secure
            then the default protocol used. 
            
            Nonexistant username login proceeds with a fake verifier to
            defy timing attacks. """
        session_id, host_info = self.current_session
        self.alert("{} attempting to login from {}. Session id: {}",
                   (username, host_info, session_id), 
                   level=self.verbosity["login_attempt"])
        if session_id in self.session_id:
            self.alert("Multiple login attempt by {} on account {} from {}", 
                       [(session_id, self.session_id[session_id]), username, 
                         host_info], level=self.verbosity["multiple_login"])
            self.logout()
            raise UnauthorizedError()
            
        database = self.database
        cursor = database.query("Credentials", 
                                retrieve_fields=("salt", "verifier"), 
                                where={"username" : username})
        registered = cursor.fetchone()
        if not registered:
            # pretend to go through login process with a fake verifier
            srp = objects["->Python->Secure_Remote_Password"]
            salt, verifier = srp.new_verifier(username, srp.new_salt(64))
            self.alert("Verifying unregistered user", 
                       level=self.verbosity["login_unregistered"])
        else:
            salt, verifier = registered      
        table_challenge = Authentication_Table.generate_challenge()
        self._table_challenge[username] = table_challenge
        response = (objects[self.protocol_component].login(username, credentials, salt, verifier),
                    table_challenge)
        return response
    
    def login_stage_two(self, username, proof_of_key, table_response):
        """ Concludes the 2 stage login process.
        
            On login failure, provides non specific information as to why.
            
            On login success, a login message and proof of the shared
            secret are returned. """  
        K, proof_of_K = objects[self.protocol_component].login(username, proof_of_key)
        login_message = self.login_fail_message
        if K:
            database = self.database
            saved_table, history = database.query("Credentials", retrieve_fields=("authentication_table", "history"),
                                                  where={"username" : username}).fetchone()          
            authentication_table = Authentication_Table.load(saved_table)
            calculation = authentication_table.get_passcode(*self._table_challenge.pop(username))
            if authentication_table.compare(calculation, table_response):
                self.alert("{} logged in".format(username), 
                        level=self.verbosity["login_success"])
                
                session_id = hkdf.hkdf(K + int(''.join(str(ord(char)) for char in history)), self.session_id_size, "session_id")                
                new_history = getattr(hashlib, self.hash_function)(session_id + ':' + history).digest()
                self.session_id[session_id] = username
                login_message = self.on_login(username)
                
                # hash the table with the entropy of K to "refresh" it
                # and update our history of shared secrets with the client                
                database.update_table("Credentials", where={"username" : username}, 
                                      arguments={"authentication_table" : hkdf.hkdf(saved_table, 256, self.hkdf_table_update_string),
                                                 "history" : new_history})               
        return (login_message, proof_of_K)
        
    def on_login(self, username):
        return self.login_message
        
    def logout(self):
        session_id, host_info = self.current_session
        username = self.session_id[session_id]
        try:
            del self.session_id[session_id]
        except KeyError:
            self.alert("Failed to logout session id {} @ {}; not logged in",
                       (session_id, host_info), 
                       level=self.verbosity["logout_failure"])
        objects["->Python->Secure_Remote_Password"].abort_login(username)
        
    def validate(self, session_id, peername, method_name):
        """ Determines whether or not the peer with the supplied
            session id is allowed to call the requested method """
        if method_name not in self.remotely_available_procedures:
            return False            
        if self.rate_limit and method_name in self.rate_limit:
            try:
                self._rate[session_id][method_name].mark()
            except KeyError:
                latency = pride.utilities.Latency("{}_{}".format(session_id, method_name))
                try:
                    self._rate[session_id][method_name] = latency
                except KeyError:
                    self._rate[session_id] = {method_name : latency}            
            current_rate = self._rate[session_id][method_name].last_measurement
            
            if current_rate < self.rate_limit[method_name]:
                self.alert("Rate of {} calls exceeded 1/{}s ({}); Denying request",
                          (method_name, self.rate_limit[method_name], current_rate),                           
                          level=self.verbosity["validate_failure"])
                return False
                
        ip = peername[0]
        if ip in self.ip_whitelist or ip not in self.ip_blacklist:
            if session_id in self.session_id or (session_id == '0' and 
                                                ((method_name in ("login", "login_stage_two") and 
                                                 self.allow_login) or
                                                (method_name == "resgiter" and
                                                 self.allow_registration))):
                self.current_session = (session_id, peername)
                self.alert("Authorizing: {} for {}", 
                          (peername, method_name), 
                          level=self.verbosity["validate_success"])
                return True
                
        self.alert(self.validation_failure_string,
                   (ip in self.ip_blacklist, session_id in self.session_id,
                    method_name, self.allow_login, self.allow_registration),
                    level=self.verbosity["validate_failure"])
        
    def __getstate__(self):
        state = super(Authenticated_Service, self).__getstate__()
        del state["database"]
        return state
        
    def on_load(self, attributes):
        super(Authenticated_Service, self).on_load(attributes)
        self._load_database()
        
        
class Authenticated_Client(pride.base.Base):
    
    defaults = {"username" : '', "password" : '', "target_service" : '',
                "password_prompt" : "{}: Please provide the pass phrase or word: ",
                "protocol_client" : "pride.srp.SRP_Client",
                "ip" : "localhost", "port" : 40022, "session_id_size" : 256,
                "auto_login" : True, "logged_in" : False,
                "hkdf_table_update_string" : "updating the authentication table",
                "hash_function" : "sha512", "history_file" : '',
                "authentication_table_file" : ''}
    
    parser_ignore = ("password_prompt", "protocol_client", "logged_in",
                     "target_service", "auto_login", "session_id_size")
    
    verbosity = {"login" : 'v', "login_stage_two" : 'v', "login_result" : 0,
                 "register" : 'v', "logout" : 0,
                 "send_proof" : 'v', "registration_success" : 0,
                 "registration_failed" : 0, "login_failed" : 0}
        
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
            username_prompt = "{}: please provide a username: ".format(self.instance_name)
            self._username = raw_input(username_prompt)
        return self._username
    def _set_username(self, value):
        self._username = value
    username = property(_get_username, _set_username)
    
    def __init__(self, **kwargs):
        super(Authenticated_Client, self).__init__(**kwargs)
        if not self.target_service:
            raise pride.errors.ArgumentError("target_service for {} not supplied".format(self))
                
        self.password_prompt = self.password_prompt.format(self.instance_name)
        self.session = self.create("pride.rpc.Session", '0', self.host_info)
        name = self.instance_name.replace("->", '_')
        self.authentication_table_file = self.authentication_table_file or "{}_auth_table.key".format(name)
        self.history_file = self.history_file or "{}_history.key".format(name)
        if self.auto_login:
            self.alert("Auto logging in", level='vv')
            self.login()
    
    def _get_username_password(self):
        return (self, self.username, self.password), {} 
        
    @with_arguments(_get_username_password)
    @remote_procedure_call(callback_name="register_results")
    def register(self, username, password): 
        """ Attempt to register username with target_service operating 
            on the machine specified by host_info. A password prompt
            will be presented if password was not passed in as an 
            attribute of the authenticated_client (recommended). """
               
    def register_results(self, success):
        """ The callback used by the register method. Proceeds to login
            upon successful registration if auto_login is True or
            an affirmative is provided by the user. """
        if success:
            assert len(success) == 16 * 16
            with open(self.authentication_table_file, "wb") as _file:
                _file.write(success)
                _file.flush()
            with open(self.history_file, "wb") as _file:
                _file.write("\x00" * 256)
                _file.flush()
            self.alert("Registered successfully", 
                       level=self.verbosity["registration_success"])
            if (self.auto_login or 
                pride.shell.get_selection("Registration success. Login now? ", bool)):
                self.login()
        else:
            self.alert("Failed to register with {};\n{}", 
                       [self.host_info, success], 
                       level=self.verbosity["registration_failed"])
            
    def _setup_login(self):
        if self.logged_in:
            self.logout()
            assert self.session.id == '0'
        password = self.password
        self._client = self.create(self.protocol_client, username=self.username,
                                   password=password)
        username, A = self._client.login()
        return (self, username, A), {}
        
    @with_arguments(_setup_login)
    @remote_procedure_call(callback_name="login_stage_two")
    def login(self, username, password_info):
        """ Attempt to log in to the target_service operating on the
            machine specified by host_info. A password prompt will be
            presented if password was not specified as an attribute of
            the authenticated_client (recommended). """
    
    def _derive_proof_of_key(self, response):
        srp_response, table_challenge = response
        self.key, self.proof_of_key = self._client.login(srp_response)
        with open(self.authentication_table_file, "a+b") as _file:
            _file.seek(0)
            bytestream = _file.read()
        table_response = Authentication_Table.load(bytestream).get_passcode(*table_challenge)
        return (self, self.username, self.proof_of_key, table_response), {}
        
    @with_arguments(_derive_proof_of_key)
    @remote_procedure_call(callback_name="login_result")
    def login_stage_two(self, username, proof_of_key, table_response): 
        """ The second stage of the login process. This is the callback
            used by login. Sends proof of key to server."""   
        
    def login_result(self, response):
        """ Calls on_login in the event of login success, provides
            an alert upon login failure. """
        try:
            message, server_proof_of_key = response
        except ValueError:
            self.alert("Unhandled exception during login {}", [response], 
                       level=0)
        else:
            if self._client.login((self.proof_of_key, server_proof_of_key, self.key)):
                self.logged_in = True
                
                with open(self.history_file, "a+b") as _file:
                    _file.seek(0)
                    history = _file.read() or "\x00" * 256
                    session_id = self.session.id = hkdf.hkdf(self.key + int(''.join(str(ord(char)) for char in history)), 
                                                             self.session_id_size, "session_id")
                    new_history = getattr(hashlib, self.hash_function)(session_id + ':' + history).digest()
                    _file.truncate(0)
                    _file.write(new_history)
                    _file.flush()
                    
                with open(self.authentication_table_file, "a+b") as _file:
                    _file.seek(0)
                    bytestream = _file.read()
                    _file.truncate(0)
                    _file.write(hkdf.hkdf(bytestream, 256, self.hkdf_table_update_string))
                    _file.flush()                         
                self.on_login(message)                               
            else:
                self.alert("Login failed", 
                           level=self.verbosity["login_failed"])           
        self._client.delete()
        self._client = None
        
    def on_login(self, message):
        """ Called automatically upon successful login. Should be
            extended by subclasses. """        
        self.alert("Login success {}", [message], 
                   level=self.verbosity["on_login"])
   
    def _reset_login_flags(self):
        self.logged_in = False
        self.session.id = '0'
        
    @call_if(logged_in=True)
    @exit(_reset_login_flags)
    @remote_procedure_call(callback=None)
    def logout(self): 
        """ Logout self.username from the target service. If the user is logged in,
            the logged_in flag will be set to False and the session.id set to '0'.
            If the user is not logged in, this is a no-op. """
        
    def delete(self):
        if self.logged_in:
            self.logout()
        super(Authenticated_Client, self).delete()
        
        
if __name__ == "__main__":        
    def test():
        service = Authenticated_Service()
        client = Authenticated_Client(username="root", target_service="Authenticated_Service", auto_login=False)
        client.register()
        #client.login()
    test()
    