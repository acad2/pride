import hkdf
import sqlite3
import getpass

import pride
import pride.base
import pride.database
import pride.utilities
import pride.shell
Instruction = pride.Instruction
objects = pride.objects

ADD_USER = "INSERT INTO Credentials VALUES(?, ?, ?)"
REMOVE_USER = "DELETE FROM Credentials WHERE username = ?"
SELECT_USER = "SELECT salt, verifier FROM Credentials WHERE username = ?"

class UnauthorizedError(Warning): pass         
                 
def derive_session_id(key, purpose='', key_size=256):
    return hkdf.hkdf(key, key_size, purpose)

def remote_procedure_call(callback=None):
    def decorate(function):
        call_name = function.__name__
        def _make_rpc(*args, **kwargs):
            self = args[0]
            self.alert("Making request '{}.{}'", (self.target_service, call_name),
                       level=self.verbosity[call_name])
            self.session.execute(Instruction(self.target_service, call_name, 
                                             *args, **kwargs), callback)
        return _make_rpc
    return decorate
  
def enter(entry_function):
    def decorate(function):
        def new_call(*args, **kwargs):
            args, kwargs = entry_function(*args, **kwargs)
            return function(*args, **kwargs)
        return new_call
    return decorate

def exit(exit_function):
    def decorate(function):
        def new_call(*args, **kwargs):
            return exit_function(function(*args, **kwargs))
        return new_call
    return decorate
    
def call_if(**conditions):
    def decorate(function):
        def new_call(*args, **kwargs):
            self = args[0]
            for key, value in conditions.items():
                if not getattr(self, key) == value:
                    break
            else:
                return function(*args, **kwargs)
        return new_call
    return decorate
    
class Authenticated_Service(pride.base.Base):
    """ Provides functionality for user registration and login, and
        provides interface for use with blacklisted/whitelisted/authenticated
        decorators. Currently uses the secure remote password protocol
        for authentication. """
    defaults = {"allow_registration" : True, "allow_login" : True,
                "protocol_component" : "->Python->Secure_Remote_Password",
                "database_name" : '', "login_message" : '',
                "current_session" : (None, None), "session_id_size" : 256,
                "validation_failure_string" : \
                   ".validate: Authorization Failure:\n    blacklisted: {}" +
                   "    session_id logged in: {}\n    method_name: '{}'\n    " +
                   "login allowed: {}    registration allowed: {}"}
    
    parser_ignore = ("protocol_component", "current_sesion", "session_id_size")
    
    verbosity = {"validate_success" : "vvv", "validate_failure" : "vv",
                 "register_attempt" : "vv", "register_success" : "vv",
                 "login_attempt" : "vv", "multiple_login" : "vv",
                 "login_success" : "vv", "login_unregistered" : "vv",
                 "logout_failure" : "vv"}
   
    rate_limit = {"login" : 2, "register" : 2}
    
    inherited_attributes = {"rate_limit" : dict}
    
    def __init__(self, **kwargs):
        self.logging_in = set()
        # maps authentication token to username
        self.session_id = {}
        self._rate = {}
        self.ip_whitelist = ["127.0.0.1", "localhost"]
        self.ip_blacklist = []
        self.method_blacklist = []
        super(Authenticated_Service, self).__init__(**kwargs)
        if not self.database_name:
            _instance_name = '_'.join(name for name in self.instance_name.split("->") if name)
            name = self.database_name = "{}_{}".format(_instance_name,
                                                       "user_registry.db")
        else:
            name = self.database_name
        self.database = self.create("database.Database", database_name=name,
                                    text_factory=str)
        self.database.create_table("Credentials", 
                                   ("username TEXT PRIMARY KEY", "salt TEXT",   
                                    "verifier BLOB"))
        self.database.commit()
                
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
                    try:
                        database.insert_into("Credentials", 
                                            (username, salt, 
                                             str(password_verifier)))
                    except sqlite3.IntegrityError as error:
                        database.alert("sqlite3 IntegrityError registering {}: {}",
                                       (username, error), level=0)
                        database.rollback()
                    else:
                        database.commit()
                        self.alert("user {} registered successfully".format(username),
                                   level=self.verbosity["register_success"])
                        return True
         
    def login(self, username, credentials):
        """ Attempt to log in as username using credentials. Due to
            implementation details it is best to call this method only
            via Authenticated_Client.login. 
            
            On login failure, provides non specific information as to why.
            Nonexistant username login proceeds with a fake verifier to
            defy timing attacks.

            On login success, a login message and proof of the shared
            secret are returned."""
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
        response = objects[self.protocol_component].login(username, credentials, salt, verifier)         
        self.logging_in.add(username)
        return response
    
    def login_stage_two(self, username, credentials):
        K, response = objects[self.protocol_component].login(username, credentials)
        self.logging_in.remove(username)
        response = (self.login_message, response)        
        #print self, "Sending response: ", response
        if K:
            self.alert("{} logged in".format(username), 
                       level=self.verbosity["login_success"])
            session_id = derive_session_id(K, "session_id", 
                                           self.session_id_size)
            self.session_id[session_id] = username        
        return response
        
    def logout(self):
        session_id, host_info = self.current_session
        username = self.session_id[session_id]
        if username in self.logging_in:
            self.logging_in.remove(username)
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
        if method_name in self.method_blacklist:
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
                                                ((method_name == "login" and 
                                                 self.allow_login) or
                                                (method_name == "resgiter" and
                                                 self.allow_registration))):
                self.current_session = (session_id, peername)
                self.alert("Authorizing: {} for {}", 
                          (self.current_session, method_name), 
                          level=self.verbosity["validate_success"])
                return True
        self.alert(self.validation_failure_string,
                   (ip in self.ip_blacklist, session_id in self.session_id,
                    method_name, self.allow_login, self.allow_registration),
                    level=self.verbosity["validate_failure"])
        
    def __getstate__(self):
        state = super(Authenticated_Service, self).__getstate__()
        del state["database"]
        del state["logging_in"]
        return state
        
    def on_load(self, attributes):
        super(Authenticated_Service, self).on_load(attributes)
        self.logging_in = set()
        self.database = self.create("database.Database", database_name=name,
                                    text_factory=str)
        self.database.create_table("Credentials", 
                                  ("username TEXT PRIMARY KEY", "salt TEXT", "verifier BLOB"))
        self.database.commit()
        
        
class Authenticated_Client(pride.base.Base):
    
    defaults = {"username" : '', "password" : '', "target_service" : '',
                "password_prompt" : "{}: Please provide the pass phrase or word: ",
                "protocol_client" : "pride.srp.SRP_Client",
                "ip" : "localhost", "port" : 40022, "session_id_size" : 256,
                "auto_login" : True, "logged_in" : False}
    
    parser_ignore = ("password_prompt", "protocol_client", "logged_in",
                     "target_service", "auto_login", "session_id_size")
    
    verbosity = {"logging_in" : 0, "on_login" : 0, "registering" : 'v',
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
                
    def __init__(self, **kwargs):
        super(Authenticated_Client, self).__init__(**kwargs)
        if not self.target_service:
            raise pride.errors.ArgumentError("target_service for {} not supplied".format(self))
        username_prompt = "{}: please provide a username: ".format(self.instance_name)
        self.username = (self.username or 
                         pride.shell.get_user_input(username_prompt,
                                                   must_reply=True))
        
        self.password_prompt = self.password_prompt.format(self.instance_name)
        self.session = self.create("pride.rpc.Session", '0', self.host_info)
        
        if self.auto_login:
            self.alert("Auto logging in", level='vv')
            self.login()
    
    @remote_procedure_call(register_results)
    def register(self, username, password): pass
        """ Attempt to register username with target_service operating 
            on the machine specified by host_info. A password prompt
            will be presented if password was not passed in as an 
            attribute of the authenticated_client (recommended). """
               
    def register_results(self, success):
        """ The callback used by the register method. Proceeds to login
            upon successful registration if auto_login is True or
            an affirmative is provided by the user. """
        if success:
            self.alert("Registered successfully", 
                       level=self.verbosity["registration_success"])
            if (self.auto_login or 
                pride.shell.get_selection("Registration success. Login now? ", bool)):
                self.login()
        else:
            self.alert("Failed to register with {};\n{}", 
                       [self.host_info, success], 
                       level=self.verbosity["registration_failed"])
    
    def _setup_login(self, *args, **kwargs):
        if self.logged_in:
            self.logout()
            assert self.session.id == '0'
            self._client = self.create(self.protocol_client, 
                                       username=self.username,
                                       password=self.password)
        return self._client.login(), {}
        
    @enter(_setup_login)
    @remote_procedure_call(callback=login_stage_two)
    def login(self):
        """ Attempt to log in to the target_service operating on the
            machine specified by host_info. A password prompt will be
            presented if password was not specified as an attribute of
            the authenticated_client (recommended). """
    
    def _derive_proof_of_key(response):
        self.key, self.proof_of_key = self._client.login(response)
        return self.username, self.proof_of_key
        
    @enter(_derive_proof_of_key)
    @remote_procedure_call(callback=login_result)
    def login_stage_2(self): pass
        """ The second stage of the login process. This is the callback
            used by login. Sends proof of key to server."""   
        
    def login_result(self, response):
        """ Calls on_login in the event of login success, provides
            an alert upon login failure. """
        try:
            message, proof = response
        except ValueError:
            self.alert("Unhandled exception during login {}", [response], 
                       level=0)
        else:
            if self._client.login((self.proof_of_key, proof, self.key)):
                self.logged_in = True
                self.session.id = derive_session_id(self.key, "session_id",
                                                    self.session_id_size)
                self.on_login(message)
            else:
                self.alert("Login failed", 
                           level=self.verbosity["login_failed"])           
        self._client.delete()
        del self._client
        
    def on_login(self, message):
        """ Called automatically upon successful login. Should be
            extended by subclasses. """        
        self.alert("Login success {}", [message], 
                   level=self.verbosity["on_login"])
   
    def _reset_login_flags(self):
        self.logged_in = False
        self.session.id = '0'
        
    @call_if(logged_in=True)
    @enter(_reset_login_flags)
    @remote_procedure_call
    def logout(self): pass
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
    