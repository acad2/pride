import pride.site_config
import pride.security

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key

def generate_rsa_keypair(public_exponent=65537, keysize=2048):
    private_key = Private_Key(public_exponent=65537, keysize=2048)
    return private_key, private_key.public_key()

class MGF(pride.base.Proxy): 

    defaults = {"hash_function" : "SHA256", "mgf_type" : "MGF1"}
    
    def __init__(self, **kwargs):
        super(MGF, self).__init__(**kwargs)
        self.wraps(getattr(padding, self.mgf_type)(getattr(hashes, self.hash_function)()))
        
        
class OAEP_Padding(pride.base.Proxy):
    
    defaults = {"hash_function" : "SHA1"}
    wrapped_object_name = "padding"
    
    def __init__(self, **kwargs):
        super(OAEP_Padding, self).__init__(**kwargs)        
        self.wraps(padding.OAEP(MGF(hash_function=self.hash_function), getattr(hashes, self.hash_function.upper())(), None))
        
        
class PSS_Padding(pride.base.Proxy):
            
    def __init__(self, **kwargs):
        super(PSS_Padding, self).__init__(**kwargs)
        self.wraps(padding.PSS(mgf=MGF(), salt_length=padding.PSS.MAX_LENGTH))
        
        
class Private_Key(pride.base.Wrapper):
    
    defaults = {"keyfile" : '', "signature_hash" : "SHA256",
                "public_exponent" : 65537, "keysize" : 2048}
    wrapped_object_name = "key"
    
    def __init__(self, **kwargs):  
        super(Private_Key, self).__init__(**kwargs)
        if self.keyfile:          
            with open(self.keyfile, "rb") as key_file:
                encoded_key = key_file.read()
            prompt = "Enter password for private key or return if key is not encrypted: "
            private_key = load_pem_private_key(encoded_key, raw_input(prompt) or None, pride.security.BACKEND)
        else:
            private_key = rsa.generate_private_key(self.public_exponent, self.keysize, pride.security.BACKEND)
        self.wraps(private_key)
                
    def signer(self):        
        return self.key.signer(PSS_Padding(), getattr(hashes, self.signature_hash.upper())())
        
    def decrypt(self, ciphertext):
        return self.key.decrypt(ciphertext, OAEP_Padding())
        
    def public_key(self):
        return Public_Key(wrapped_object=self.key.public_key())
        
        
class Public_Key(pride.base.Wrapper):
    
    defaults = {"signature_hash" : "SHA256"}
    wrapped_object_name = "key"
    
    def verifier(self, signature):        
        return self.key.verifier(signature, PSS_Padding(), getattr(hashes, self.signature_hash.upper())())                                 
        
    def encrypt(self, plaintext):
        return self.key.encrypt(plaintext, OAEP_Padding())
    
    
def test_private_public_key():
    private_key, public_key = generate_rsa_keypair()
    message = "Test message!"
    ciphertext = public_key.encrypt(message)
    plaintext = private_key.decrypt(ciphertext)
    assert plaintext == message
        
    signer = private_key.signer()
    signer.update(message)
    signature = signer.finalize()
    
    verifier = public_key.verifier(signature)
    assert verifier.verify()
    
if __name__ == "__main__":
    test_private_public_key()
    