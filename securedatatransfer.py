import pride.datatransfer
import pride.crypto.micklhdh as micklhdh

class Secure_Data_Transfer_Client(pride.datatransfer.Data_Transfer_Client):
    
    defaults = {"parameters" : micklhdh.system_parameters_128}
    
    def __init__(self, **kwargs):
        super(Secure_Data_Transfer_Client, self).__init__(**kwargs)
        self.public_key, self.private_key = micklhdh.generate_keypair(*self.parameters)
        
    def receive(self, messages):
        for sender, message in messages:
            request, arguments = message.split(' ', 1)            
            self.alert(message, level=0)
            if request == "begin_exchange":          
                public_key = self.deserealize(arguments)
                
                ephemeral_key, token = self.begin_exchange(arguments)
                self.send_to(sender, "continue_exchange " + self.public_key + token)
                self.ephemeral_key_for[sender] = ephemeral_key
                
            elif request == "continue_exchange":
                end_of_public_key = self.public_key_size_bytes
                sender_public_key = self.deserealize(arguments[:end_of_public_key])
                sender_token = self.deserealize(arguments[end_of_public_key:])
                
                token, shared_secret = self.continue_exchange(sender, sender_public_key, sender_token)
                self.secret_for[sender] = shared_secret
                self.send_to(sender, "finish_exchange " + self.public_key + token)
                self.alert(self.secret_for[sender], 0)
                
            elif request == "finish_exchange":
                sender_public_key = self.deserealize(arguments[:end_of_public_key])
                sender_token = self.deserealize(arguments[end_of_public_key:])
                
                ephemeral_key = self.ephemeral_key_for[sender]
                self.secret_for[sender] = self.finish_exchange(ephemeral_key, sender_public_key, sender_token)
                del self.ephemeral_key_for[sender]
                self.alert(self.secret_for[sender], 0)
            else:
                raise NotImplementedError()
    
    def deserealize(self, serialized_object):
        return bytes_to_integer(serialized_object)
        
    def secure_channel_to(self, sender):
        private_key, public_key = self.keypair
        self.send_to("sender", "begin_exchange " + public_key)
        
    def begin_exchange(self, other_public_key):
        ephemeral_key = self.create_ephemeral_key()        
        token = self.create_token(ephemeral_key, other_public_key)
        return (ephemeral_key, token)
        
    def create_token(self, ephemeral_key, public_key):
        return micklhdh.advance_key_exchange(public_key, self.private_key, ephemeral_key, self.p)
        
    def create_ephemeral_key(self):
        return micklhdh.initiate_key_exchange(*self.system_parameters)
        
        
    def continue_exchange(self, others_public_key, token):
        ephemeral_key, self_token = self.begin_exchange(others_public_key)
        shared_secret = self.generate_shared_secret(ephemeral_key, others_public_key)
        return (self_token, shared_secret)
        
        
def test_secure_data_transfer_client():
    client1 = Secure_Data_Transfer_Client(username="Ella!")
    client2 = Secure_Data_Transfer_Client(username="NotElla!")
    
    client1.secure_channel_to("NotElla!")
    
if __name__ == "__main__":
    test_secure_data_transfer_client()
    
    