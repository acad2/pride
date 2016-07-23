import pride.authentication2

class Rpc_Hello_World_Service(pride.authentication2.Authenticated_Service):
    
    remotely_available_procedures = ("hello_world", )
    
    def hello_world(self, argument, *args, **kwargs):                
        return "Hello world" + ' ' + argument
        

class Rpc_Hello_World_Client(pride.authentication2.Authenticated_Client):
            
    defaults = {"target_service" : "/Rpc_Hello_World_Service"}
    
    @pride.authentication2.remote_procedure_call(callback_name="alert")
    def hello_world(self, argument, *args, **kwargs):
        pass
        
def test_hello_world_rpc():
    service = Rpc_Hello_World_Service()
    client = Rpc_Hello_World_Client(username="Ella")
    
    client.hello_world("I'm an argument!", "I work with any number of arguments", 1, 2, 3, testing=True)
    
if __name__ == "__main__":
    test_hello_world_rpc()
    