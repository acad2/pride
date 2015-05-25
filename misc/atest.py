import mpre.base
import mpre.userinput
Instruction = mpre.Instruction

class Authenticated_Service(mpre.base.Base):

    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"allow_registration" : True})
    
    def __init__(self, **kwargs):
        self.user_key = {}
        self.logging_in = set()
        super(Authenticated_Service, self).__init__(**kwargs)
        
    def register(self, username, password):
        if self.allow_registration:
            if components["Secure_Remote_Password"].register(username, password):
                return True
                
    def login(self, username, credentials):
        self.alert("In login {} {}", [username, credentials], level=0)
        response = components["Secure_Remote_Password"].login(username, credentials)        
        if username in self.logging_in:
            K, response = response
            self.user_key[username] = K
            self.logging_in.remove(username)
        else:
            self.logging_in.add(username)
        return response
        
    
class Authenticated_Client(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"username" : '',
                     "target_service" : '',
                     "host_info" : ("0.0.0.0", 40022),
                     "auto_login" : True})
    
    def __init__(self, **kwargs):
        super(Authenticated_Client, self).__init__(**kwargs)
        if not self.username or not self.target_service:
            raise mpre.errors.ArgumentError("username or target_service not supplied")
        if self.auto_login:
            self.login()
            
    def register(self): 
        self.alert("Registering", level=0)
        Instruction(self.target_service, "register", 
                    "root", "password").execute(host_info=self.host_info,
                                                callback=self.register_results)
               
    def register_results(self, success):
        if success:
            if (self.auto_login or 
                mpre.userinput.get_selection("Registration success. Login now? ", bool)):
                self.login()
        else:
            self.alert("Failed to register with {};\n{}", [self.host_info, success])
    
    def login(self):
        self.alert("Logging in...", level=0)
        self.client = self.create("mpre.misc.srp.SRP_Client", username=self.username)  
        Instruction(self.target_service, "login", 
                    *self.client.login()).execute(host_info=self.host_info,
                                                  callback=self.send_proof)    
                                                  
    def send_proof(self, response):
        self.key, self.proof_of_key = self.client.login(response)
        Instruction(self.target_service, "login", self.username,
                    self.proof_of_key).execute(host_info=self.host_info,
                                               callback=self.login_result)
                                                         
    def login_result(self, response):
        if self.client.login((self.proof_of_key, response, self.key)):
            self.on_login()
        else:
            self.alert("Login failed: {}", [response], level=0)
            if "register" in response:
                self.register()            
            
    def on_login(self):
        pass
        
def test():
    service = Authenticated_Service()
    client = Authenticated_Client(username="root", target_service="Authenticated_Service")
    #client.register()
    client.login()
    
if __name__ == "__main__":
    mpre.components["Metapython"].create("mpre.misc.srp.Secure_Remote_Password")
    test()