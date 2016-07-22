import pride.datatransfer
import pride.crypto.micklhdh as micklhdh
from pride.crypto.utilities import bytes_to_integer, integer_to_bytes

class Secure_Data_Transfer_Client(pride.datatransfer.Data_Transfer_Client):
    
    defaults = {"parameters" : micklhdh.system_parameters_128}
    verbosity = {"secure_channel_to" : 0, "begin_exchange" : 0, "continue_exchange" : 0, 
                 "finish_exchange" : 0}
    mutable_defaults = {"ephemeral_key_for" : dict, "secret_for" : dict}
    
    def _get_p(self):
        return self.parameters[1]
    p = property(_get_p)
    
    def _get_public_key_size(self):
        return len(self.serialize(self.parameters[0]))
    public_key_size = property(_get_public_key_size)
    
    def __init__(self, **kwargs):
        super(Secure_Data_Transfer_Client, self).__init__(**kwargs)
        with open("{}_keypair.key".format(self.reference.replace('/', '_')), 'a+b') as _file:
            _file.seek(0)
            serialized_keys = _file.read()
            if not serialized_keys:
                public_key, private_key = micklhdh.generate_keypair(*self.parameters)
                _file.write(self.serialize(public_key))
                _file.write(self.serialize(private_key))
            else:
                keysize = self.public_key_size
                public_key = self.deserialize(serialized_keys[:keysize])
                private_key = self.deserialize(serialized_keys[keysize:])
        self.public_key, self.private_key = public_key, private_key      
        
    def receive(self, messages):
        for sender, message in messages:            
            request, arguments = message.split(' ', 1)            
            self.alert(message, level=0)
            if request == "begin_exchange":        
                self.alert("Beginning exchange with: {}".format(sender), level=self.verbosity["begin_exchange"])
                public_key = self.deserialize(arguments)
                
                ephemeral_key, token = self.begin_exchange(public_key)
                self.send_to(sender, "continue_exchange " + self.serialize(self.public_key) + self.serialize(token))
                self.ephemeral_key_for[sender] = ephemeral_key
                
            elif request == "continue_exchange":
                self.alert("Participating in key exchange with {}".format(sender), level=self.verbosity["continue_exchange"])
                end_of_public_key = self.public_key_size
                sender_public_key = self.deserialize(arguments[:end_of_public_key])
                sender_token = self.deserialize(arguments[end_of_public_key:])
                
                token, shared_secret = self.continue_exchange(sender_public_key, sender_token)
                self.secret_for[sender] = shared_secret
                self.send_to(sender, "finish_exchange " + self.serialize(self.public_key) + self.serialize(token))               
                print("Established secret: {}".format(self.secret_for[sender]))
                
            elif request == "finish_exchange":
                self.alert("Finishing exchange with: {}".format(sender), level=self.verbosity["finish_exchange"])
                
                end_of_public_key = self.public_key_size
                sender_public_key = self.deserialize(arguments[:end_of_public_key])
                sender_token = self.deserialize(arguments[end_of_public_key:])
                
                ephemeral_key = self.ephemeral_key_for[sender]
                self.secret_for[sender] = self.generate_shared_secret(sender_token, ephemeral_key)
                del self.ephemeral_key_for[sender]
                print("Established secret: {}".format(self.secret_for[sender]))
            else:
                raise NotImplementedError()
    
    def deserialize(self, serialized_object):
        return bytes_to_integer(bytearray(serialized_object))
        
    def serialize(self, key_or_token):
        return bytes(integer_to_bytes(key_or_token))
        
    def create_token(self, ephemeral_key, public_key):
        return micklhdh.advance_key_exchange(public_key, self.private_key, ephemeral_key, self.p)
        
    def create_ephemeral_key(self):
        return micklhdh.initiate_key_exchange(*self.parameters)
        
    def secure_channel_to(self, sender):        
        self.alert("Securing channel to: {}".format(sender), level=self.verbosity["secure_channel_to"])
        self.send_to(sender, "begin_exchange " + self.serialize(self.public_key))
        
    def begin_exchange(self, other_public_key):
        ephemeral_key = self.create_ephemeral_key()        
        token = self.create_token(ephemeral_key, other_public_key)
        return (ephemeral_key, token)              
        
    def continue_exchange(self, others_public_key, token):
        ephemeral_key, self_token = self.begin_exchange(others_public_key)
        shared_secret = self.generate_shared_secret(token, ephemeral_key)
        return (self_token, shared_secret)        
     
    def generate_shared_secret(self, others_token, ephemeral_key):
        return micklhdh.generate_shared_secret(others_token, ephemeral_key, self.p)
        
def test_secure_data_transfer_client():
    client1 = Secure_Data_Transfer_Client(username="Ella!")
    client2 = Secure_Data_Transfer_Client(username="NotElla!")
    
    client1.secure_channel_to("NotElla!")
    
if __name__ == "__main__":
    test_secure_data_transfer_client()
    
    