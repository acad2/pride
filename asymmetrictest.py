import pride.base
import pride.security

import cryptography.exceptions
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key

def generate_rsa_keypair(public_exponent=65537, keysize=2048):
    private_key = RSA_Private_Key(public_exponent=65537, keysize=2048)
    return private_key, private_key.public_key()

def generate_ec_keypair(curve_name="SECP384R1", hash_algorithm="SHA256"):
    private_key = EC_Private_Key(curve_name=curve_name, hash_algorithm=hash_algorithm)
    return private_key, private_key.public_key()
    
class MGF(pride.base.Proxy): 

    defaults = {"hash_function" : "SHA256", "mgf_type" : "MGF1"}
    
    def __init__(self, **kwargs):
        super(MGF, self).__init__(**kwargs)
        self.wraps(getattr(padding, self.mgf_type)(getattr(hashes, self.hash_function)()))
        
        
class OAEP_Padding(pride.base.Proxy):
    
    defaults = {"hash_function" : "SHA1"} # only available option by default
    wrapped_object_name = "padding"
    
    def __init__(self, **kwargs):
        super(OAEP_Padding, self).__init__(**kwargs)        
        self.wraps(padding.OAEP(MGF(hash_function=self.hash_function), getattr(hashes, self.hash_function.upper())(), None))
        
        
class PSS_Padding(pride.base.Proxy):
            
    def __init__(self, **kwargs):
        super(PSS_Padding, self).__init__(**kwargs)
        self.wraps(padding.PSS(mgf=MGF(), salt_length=padding.PSS.MAX_LENGTH))
        
        
class RSA_Private_Key(pride.base.Wrapper):
    
    defaults = {"keyfile" : '', "signature_hash" : "SHA256",
                "public_exponent" : 65537, "keysize" : 2048}
    wrapped_object_name = "key"
    
    def __init__(self, **kwargs):  
        super(RSA_Private_Key, self).__init__(**kwargs)
        if self.keyfile:          
            with open(self.keyfile, "rb") as key_file:
                encoded_key = key_file.read()
            prompt = "Enter password for private key or return if key is not encrypted: "
            private_key = load_pem_private_key(encoded_key, raw_input(prompt) or None, pride.security.BACKEND)
        else:
            private_key = rsa.generate_private_key(self.public_exponent, self.keysize, pride.security.BACKEND)
        self.wraps(private_key)
     
    def sign(self, message):
        signer = self.signer()
        signer.update(message)
        return signer.finalize()
        
    def signer(self):        
        return self.key.signer(PSS_Padding(), getattr(hashes, self.signature_hash.upper())())
        
    def decrypt(self, ciphertext):
        return self.key.decrypt(ciphertext, OAEP_Padding())
        
    def public_key(self):
        return RSA_Public_Key(wrapped_object=self.key.public_key())
        
        
class RSA_Public_Key(pride.base.Wrapper):
    
    defaults = {"signature_hash" : "SHA256"}
    wrapped_object_name = "key"
    required_attributes = ("wrapped_object", )
    
    def verify(self, signature, message):
        verifier = self.verifier(signature)
        verifier.update(message)
        try:
            verifier.verify()
        except cryptography.exceptions.InvalidSignature:
            return False
        else:
            return True
        
    def verifier(self, signature):        
        return self.key.verifier(signature, PSS_Padding(), getattr(hashes, self.signature_hash.upper())())                                 
        
    def encrypt(self, plaintext):
        return self.key.encrypt(plaintext, OAEP_Padding())
    

class EC_Private_Key(pride.base.Wrapper):
    
    defaults = {"curve_name" : "SECP384R1", "hash_algorithm" : "SHA256"}
    wrapped_object_name = "key"
    
    def __init__(self, **kwargs):
        super(EC_Private_Key, self).__init__(**kwargs)        
        private_key = ec.generate_private_key(getattr(ec, self.curve_name), pride.security.BACKEND)
        self.wraps(private_key)
        
    def sign(self, message):
        signer = self.signer()
        signer.update(message)
        return signer.finalize()
        
    def signer(self):
        return self.key.signer(ec.ECDSA(getattr(hashes, self.hash_algorithm)()))
        
    def public_key(self):
        return EC_Public_Key(wrapped_object=self.key.public_key())
        
    def exchange(self, public_key):
        return self.key.exchange(ec.ECDH(), public_key)
        
        
class EC_Public_Key(pride.base.Wrapper):
            
    defaults = {"serialization_encoding" : "pem", "serialization_format" : "SubjectPublicKeyInfo",
                "hash_algorithm" : "SHA256"}
    wrapped_object_name = "key"
    
    def verify(self, signature, message):
        verifier = self.verifier(signature)
        verifier.update(message)
        try:
            verifier.verify()
        except cryptography.exceptions.InvalidSignature:
            return False
        else:
            return True
            
    def verifier(self, signature):
        return self.key.verifier(signature, ec.ECDSA(getattr(hashes, self.hash_algorithm)()))
        
    def public_bytes(self):
        encoding = getatttr(cryptography.hazmat.primitives.serialization, self.serialization_encoding)
        _format = getattr(cryptography.hazmat.primitives.serialization, self.serialization_format)
        return self.key.public_bytes(encoding, _format)
            
def test_rsa():
    private_key, public_key = generate_rsa_keypair()
    message = "Test message!"
    ciphertext = public_key.encrypt(message)
    plaintext = private_key.decrypt(ciphertext)
    assert plaintext == message
        
    signature = private_key.sign(message)
    assert public_key.verify(signature, message)    
       
def test_ecc():
    private_key, public_key = generate_ec_keypair()
    message = "Test message"
    signature = private_key.sign(message)
    assert public_key.verify(signature, message)
    
    private_key2, public_key2 = generate_ec_keypair()
    shared_secret = private_key.exchange(public_key2)
    shared_secret2 = private_key2.exchange(public_key)
    assert shared_secret == shared_secret2
    
if __name__ == "__main__":
    test_rsa()
    test_ecc()
    