import sqlite3
import getpass

import mpre
import mpre.base
import mpre.utilities
Instruction = mpre.Instruction
objects = mpre.objects

ADD_USER = "INSERT INTO Credentials VALUES(?, ?, ?)"
REMOVE_USER = "DELETE FROM Credentials WHERE username = ?"
SELECT_USER = "SELECT salt, verifier FROM Credentials WHERE username = ?"

class UnauthorizedError(Warning): pass

def blacklisted(function):
    def call(instance, *args, **kwargs):
        if instance.requester_address in instance.blacklist:
            instance.alert("{} {}".format(UnauthorizedError("Denied blacklisted client"), instance.requester_address), level='v')
        else:
            return function(instance, *args, **kwargs)
    
    return call
    
def whitelisted(function):
    def call(instance, *args, **kwargs):
        if instance.requester_address not in instance.whitelist:            
            instance.alert("{} {}".format(UnauthorizedError("Denied non whitelisted client"), instance.requester_address), level=0)#'v')
        else:
            return function(instance, *args, **kwargs)
            
    return call
    
def authenticated(function):
    def call(instance, *args, **kwargs):
        if instance.requester_address not in instance.logged_in:
            self.alert("{} {}".format(UnauthorizedError("not logged in"), instance.requester_address), level='v')
        else:
            return function(instance, *args, **kwargs)
        
    return call    

        
class Authenticated_Service(mpre.base.Base):
    """ Warning: not yet secure by any means"""
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"allow_registration" : True,
                     "protocol_component" : "Secure_Remote_Password",
                     "database_filename" : "user_registry",
                     "login_message" : '',
                     "requester_address" : 'localhost'})
    
    def __init__(self, **kwargs):
        self.user_secret = {} # maps username to shared secret
        self.logging_in = set()
        self.logged_in = mpre.utilities.Reversible_Mapping() # maps host info to username
        self.whitelist = ["127.0.0.1", "localhost"]
        self.blacklist = []
        super(Authenticated_Service, self).__init__(**kwargs)
        
        self.database_filename = "{}_{}".format(self.instance_name, self.database_filename)
        database = self.database = sqlite3.connect(self.database_filename)
        cursor = database.cursor()        
        cursor.execute("CREATE TABLE IF NOT EXISTS Credentials(" + 
                       "username TEXT PRIMARY KEY, salt TEXT, verifier BLOB)")      
        database.commit()
        
    def register(self, username, password):        
        self.alert("Attempting to register '{}'", [username], level='v')
        if self.allow_registration:
            database = sqlite3.connect(self.database_filename)
            database.text_factory = str
            cursor = database.cursor()
            cursor.execute(SELECT_USER, (username, ))
            registered = cursor.fetchone()
            
            if not registered:       
                salt, password_verifier = objects["Secure_Remote_Password"].new_verifier(username, password)            
                try:
                    cursor.execute(ADD_USER, (username, salt, str(password_verifier)))
                except sqlite3.IntegrityError:
                    self.alert("Attempted to register an already existing user '{}'", 
                               [username], level='v')
                    database.rollback()
                else:
                    database.commit()
                database.close()                
                return True
         
    def login(self, username, credentials):
        if username in self.user_secret:
            self.alert("Detected multiple login attempt on account {}", [username], level='v')
        
        if username in self.logging_in:
            K, response = objects[self.protocol_component].login(username, credentials)
            if K:
                self.user_secret[username] = K
                self.logged_in[self.requester_address] = username
                self.logging_in.remove(username)
                response = (self.login_message, response)
            else:
                response = (K, response)
        else:
            database = sqlite3.connect(self.database_filename)
            database.text_factory = str
            cursor = database.cursor()
            
            cursor.execute(SELECT_USER, (username, ))
            registered = cursor.fetchone()
            if not registered:
                # pretend to go through login process with a fake verifier
                salt, verifier = s, v = self.new_verifier(username, self.new_salt(64))
                self.alert("Verifying unregistered user", level=0)
            else:
                salt, verifier = s, v = registered
            
            response = objects[self.protocol_component].login(username, credentials, salt, verifier)        
            self.logging_in.add(username)
        return response
        
    
class Authenticated_Client(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"username" : '',
                     "password" : '',
                     "target_service" : '',
                     "password_prompt" : "Please provide the pass phrase or word: ",
                     "protocol_client" : "mpre.srp.SRP_Client",
                     "host_info" : ("localhost", 40022),
                     "auto_login" : True,
                     "logged_in" : False})
    
    parser_ignore = mpre.base.Base.parser_ignore + ("password_prompt", "protocol_client", "logged_in")
    
    def __init__(self, **kwargs):
        super(Authenticated_Client, self).__init__(**kwargs)
        self.username = self.username or mpre.userinput.get_user_input("Please provide a username: ")
        if not self.target_service:
            raise mpre.errors.ArgumentError("target_service not supplied")
        if self.auto_login:
            self.login()
            
    def register(self): 
        self.alert("Registering", level=0)
        Instruction(self.target_service, "register", self.username, 
                    self.password or getpass.getpass(self.password_prompt)).execute(host_info=self.host_info,
                                                                                    callback=self.register_results)
               
    def register_results(self, success):
        if success:
            if (self.auto_login or 
                mpre.userinput.get_selection("Registration success. Login now? ", bool)):
                self.login()
        else:
            self.alert("Failed to register with {};\n{}", [self.host_info, success], level=0)
    
    def login(self):
        self.alert("Logging in...", level=0)
        self.client = self.create(self.protocol_client, username=self.username, password=self.password)
        Instruction(self.target_service, "login", 
                    *self.client.login()).execute(host_info=self.host_info,
                                                  callback=self.send_proof)    
                                                  
    def send_proof(self, response):
        self.key, self.proof_of_key = self.client.login(response)
        Instruction(self.target_service, "login", self.username,
                    self.proof_of_key).execute(host_info=self.host_info,
                                               callback=self.login_result)
                                                         
    def login_result(self, response):
        try:
            message, proof = response
        except ValueError:
            self.alert("Unhandled exception during login {}", [response], level=0)
        else:
            if self.client.login((self.proof_of_key, proof, self.key)):
                self.on_login(message)
            else:
                self.alert("Login failed", level=0)           
        self.client.delete()
        del self.client
        
    def on_login(self, message):
        self.logged_in = True
        self.alert("Login success {}", [message], level=0)

if __name__ == "__main__":        
    def test():
        service = Authenticated_Service()
        client = Authenticated_Client(username="root", target_service="Authenticated_Service", auto_login=False)
        client.register()
        #client.login()
    test()
    