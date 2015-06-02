import getpass

import mpre
import mpre.base
Instruction = mpre.Instruction
components = mpre.components

class UnauthorizedError(Warning): pass

def Authenticated(function):
    def call(instance, *args, **kwargs):
        if components["RPC_Server"].requester_address not in instance.logged_in:
            raise UnauthorizedError("not logged in")
        return function(instance, *args, **kwargs)
        
    return call    

class Authenticated_Service(mpre.base.Base):

    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"allow_registration" : True,
                     "protocol_component" : "Secure_Remote_Password",
                     "database_filename" : "user_registry",
                     "login_message" : ''})
    
    def __init__(self, **kwargs):
        self.user_secret = {} # maps username to shared secret
        self.logging_in = set()
        self.logged_in = {} # maps host info to username
        super(Authenticated_Service, self).__init__(**kwargs)
                       
    def register(self, username, password):        
        self.alert("Attempting to register '{}'", [username], level='v')
        if self.allow_registration:
            registered = components[self.protocol_component].register(username, password)
            if registered:
                return True
         
    def login(self, username, credentials):
        if username in self.user_secret:
            self.alert("Detected multiple login attempt on account {}", [username], level='v')
        response = components[self.protocol_component].login(username, credentials)
        if username in self.logging_in:
            K, response = response
            self.user_secret[username] = K
            self.logged_in[components["RPC_Server"].requester_address] = username
            self.logging_in.remove(username)
            response = (self.login_message, response)
        else:
            self.logging_in.add(username)
        return response
        
    
class Authenticated_Client(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"username" : '',
                     "target_service" : '',
                     "password_prompt" : "Please provide the pass phrase or word: ",
                     "protocol_client" : "mpre.srp.SRP_Client",
                     "host_info" : ("localhost", 40022),
                     "auto_login" : True,
                     "logged_in" : False})
    
    def __init__(self, **kwargs):
        super(Authenticated_Client, self).__init__(**kwargs)
        if not self.username or not self.target_service:
            raise mpre.errors.ArgumentError("username or target_service not supplied")
        if self.auto_login:
            self.login()
            
    def register(self): 
        self.alert("Registering", level=0)
        Instruction(self.target_service, "register", self.username, 
                    getpass.getpass(self.password_prompt)).execute(host_info=self.host_info,
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
        self.client = self.create(self.protocol_client, username=self.username)
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
    