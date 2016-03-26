import pride.datatransfer
import pride.security
import pride.asymmetrictest

from cryptography.hazmat.primitives.serialization import load_pem_public_key

class Secure_Data_Transfer_Client(pride.datatransfer.Data_Transfer_Client):
    
    defaults = {"ecdh_curve_name" : "SECP384R1", "keysize" : 384}
    mutable_defaults = {"key_for" : dict}
    
    def new_keypair(self):
        return pride.asymmetrictest.generate_ec_keypair(self.ecdh_curve_name, self.keysize)
        
    def initiate_key_exchange(self, username):
        private_key, public_key = self.new_keypair()
        self.key_for[username] = private_key
        self.send_to(username, "exchange_public_key " + public_key.public_bytes())
        
    def receive(self, messages):
        for sender, message in messages:
            request, arguments = message.split(' ', 1)
            senders_public_key = load_pem_public_key(arguments, pride.security.BACKEND)
            self.alert(message, level=0)
            if request == "exchange_public_key":                                                
                private_key, public_key = self.new_keypair()
                self.send_to(sender, "exchange_secret " + public_key.public_bytes())
                
                shared_secret = private_key.exchange(senders_public_key)
                self.alert(shared_secret, level=0)
                
            elif request == "exchange_secret ":
                shared_secret = self.key_for[username].exchange(senders_public_key)
                self.alert(shared_secret, level=0)
            else:
                raise NotImplementedError()
                
def test_secure_data_transfer_client():
    import pride
    client = Secure_Data_Transfer_Client(username="localhost", token_file_encrypted=False, token_file_indexable=True)
    client2 = Secure_Data_Transfer_Client(username="someone_else", token_file_encrypted=False, token_file_indexable=True)
    pride.Instruction(client.reference, "initiate_key_exchange", "someone_else").execute(priority=1)
    pride.Instruction(client2.reference, "refresh").execute(priority=2)
    
if __name__ == "__main__":
    test_secure_data_transfer_client()
    