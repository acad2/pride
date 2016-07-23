import pride.authentication2

class Rpc_Hello_World_Service(pride.authentication2.Authenticated_Service):
    
    remotely_available_procedures = ("hello_world", )
    
    def hello_world(self):
        return "Hello world"
        

class Rpc_Hello_World_Client(pride.authentication2.Authenticated_Client):
            
    defaults = {"target_service" : "/Rpc_Hello_World_Service"}
    
    @pride.authentication2.remote_procedure_call(callback_name="alert")
    def hello_world(self):
        pass
        
def test_hello_world_rpc():
    service = Rpc_Hello_World_Service()
    client = Rpc_Hello_World_Client(username="Ella")
    
    client.hello_world()
    
if __name__ == "__main__":
    test_hello_world_rpc()
    