import hkdf
import sqlite3
import getpass

import mpre
import mpre.base
import mpre.database
import mpre.utilities
import mpre.shell
Instruction = mpre.Instruction
objects = mpre.objects

ADD_USER = "INSERT INTO Credentials VALUES(?, ?, ?)"
REMOVE_USER = "DELETE FROM Credentials WHERE username = ?"
SELECT_USER = "SELECT salt, verifier FROM Credentials WHERE username = ?"

class UnauthorizedError(Warning): pass         
                 
def derive_session_id(key, purpose='', key_size=256):
    return hkdf.hkdf(key, key_size, purpose)

        
class Authenticated_Service(mpre.base.Base):
    """ Provides functionality for user registration and login, and
        provides interface for use with blacklisted/whitelisted/authenticated
        decorators. Currently uses the secure remote password protocol
        for authentication. 
        
        Note that authentication is not automatically required for all
        method calls on an Authenticated_Service object. Each method must
        be decorated explicitly with the access controls desired."""
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"allow_registration" : True,
                     "protocol_component" : "Secure_Remote_Password",
                     "database_name" : '',
                     "login_message" : '',
                     "current_session" : (None, None),
                     "session_id_size" : 256})
    
    def __init__(self, **kwargs):
        self.logging_in = set()
        # maps authentication token to username
        self.session_id = {}
        self.ip_whitelist = ["127.0.0.1", "localhost"]
        self.ip_blacklist = []
        self.method_blacklist = []
        super(Authenticated_Service, self).__init__(**kwargs)
        name = self.database_name = (self.database_name or 
                                     "{}_{}".format(self.instance_name, 
                                                    "user_registry.db"))
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
        self.alert("Attempting to register '{}'", [username], level='v')
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
                    salt, password_verifier = objects["Secure_Remote_Password"].new_verifier(username, password) 
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
                   (username, host_info, session_id), level='v')
        if session_id in self.session_id:
            self.alert("Multiple login attempt by {} on account {} from {}", 
                       [(session_id, self.session_id[session_id]), username, 
                         host_info], level='v')
            self.logout()
            raise UnauthorizedError()
            
        if username in self.logging_in:
            K, response = objects[self.protocol_component].login(username, credentials)
            self.logging_in.remove(username)
            response = (self.login_message, response)        
            #print self, "Sending response: ", response
            if K:
                self.alert("{} logged in".format(username), level='vv')
                session_id = derive_session_id(K, "session_id", 
                                               self.session_id_size)
                self.session_id[session_id] = username
        else:
            database = self.database
            cursor = database.query("Credentials", 
                                    retrieve_fields=("salt", "verifier"), 
                                    where={"username" : username})
            registered = cursor.fetchone()
            if not registered:
                # pretend to go through login process with a fake verifier
                srp = objects["Secure_Remote_Password"]
                salt, verifier = srp.new_verifier(username, srp.new_salt(64))
                self.alert("Verifying unregistered user", level='v')
            else:
                salt, verifier = registered
                        
            response = objects[self.protocol_component].login(username, credentials, salt, verifier)         
            self.logging_in.add(username)
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
                       (session_id, host_info), level='vv')
        $Secure_Remote_Password.abort_login(username)
        
    def validate(self, session_id, peername, method_name):
        if method_name in self.method_blacklist:
            return False
            
        ip = peername[0]
        permission = False
   #     if ip in ("localhost", "127.0.0.1"):
   #         permission = True  
   #         print "Giving permission because it's localhost"
        if ip in self.ip_whitelist or ip not in self.ip_blacklist:
            #print "Checking: " * 3, session_id, method_name
            if session_id in self.session_id or (session_id == '0' and 
                                                ((method_name == "login" and 
                                                 self.allow_login) or
                                                (method_name == "resgiter" and
                                                 self.allow_registration))):
            #    print "Permission granted"
                #permission = True        
       # if permission:
                self.current_session = (session_id, peername)
                self.alert("Authorizing: {} for {}", 
                        (self.current_session, method_name), level='vv')
                return True
            #else:
            #    print "Denied"
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
        
        
class Authenticated_Client(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"username" : '',
                     "password" : '',
                     "target_service" : '',
                     "password_prompt" : "{}: Please provide the pass phrase or word: ",
                     "protocol_client" : "mpre.srp.SRP_Client",
                     "ip" : "localhost", 
                     "port" : 40022,
                     "auto_login" : True,
                     "logged_in" : False,
                     "session_id_size" : 256})
    
    parser_ignore = mpre.base.Base.parser_ignore + ("password_prompt", "protocol_client", "logged_in")
    
    verbosity = {"logging_in" : 'v',
                 "on_login" : 'v',
                 "registering" : 'v',
                 "send_proof" : 'v',
                 "registration_success" : '',
                 "registration_failed" : 0,
                 "login_failed" : 0}
        
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
            raise mpre.errors.ArgumentError("target_service for {} not supplied".format(self))
        username_prompt = "{}: please provide a username: ".format(self.instance_name)
        self.username = (self.username or 
                         mpre.shell.get_user_input(username_prompt,
                                                   must_reply=True))
        
        self.password_prompt = self.password_prompt.format(self.instance_name)
        self.session = self.create("mpre.rpc.Session", '0', self.host_info)
        
        if self.auto_login:
            self.alert("Auto logging in", level='vv')
            self.login()
            
    def register(self): 
        """ Attempt to register username with target_service operating 
            on the machine specified by host_info. A password prompt
            will be presented if password was not passed in as an 
            attribute of the authenticated_client (recommended). """
        self.alert("Registering", level=self.verbosity["registering"])
        self.session.execute(Instruction(self.target_service, "register", 
                                         self.username, self.password), 
                             self.register_results)
               
    def register_results(self, success):
        """ The callback used by the register method. Proceeds to login
            upon successful registration if auto_login is True or
            an affirmative is provided by the user. """
        if success:
            self.alert("Registered successfully", 
                       level=self.verbosity["registration_success"])
            if (self.auto_login or 
                mpre.shell.get_selection("Registration success. Login now? ", bool)):
                self.login()
        else:
            self.alert("Failed to register with {};\n{}", 
                       [self.host_info, success], 
                       level=self.verbosity["registration_failed"])
    
    def login(self):
        """ Attempt to log in to the target_service operating on the
            machine specified by host_info. A password prompt will be
            presented if password was not specified as an attribute of
            the authenticated_client (recommended). """
        if self.logged_in:
            self.logout()
            assert self.session.id == '0'
        self.alert("Logging in...", level=self.verbosity["logging_in"])
        self._client = self.create(self.protocol_client, 
                                   username=self.username,
                                   password=self.password)
        self.session.execute(Instruction(self.target_service, "login", 
                                         *self._client.login()),
                             self.send_proof)
                                                  
    def send_proof(self, response):
        """ The second stage of the login process. This is the callback
            used by login. Sends proof of key to server."""
        self.alert("Sending proof of key", level=self.verbosity["send_proof"])
        self.key, self.proof_of_key = self._client.login(response)
        self.session.execute(Instruction(self.target_service, "login", 
                                         self.username, self.proof_of_key),
                             self.login_result)       
        
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
                   
    def logout(self):
        if self.logged_in:
            self.logged_in = False
            self.session.execute(Instruction(self.target_service, "logout"), None)
            self.session.id = '0'
            
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
    