""" A python implementation of hmac-based extract-and-expand key derivation function (HKDF).
    
    usage:
        
        hkdf.hkdf(input_keying_material, length, info='', salt='', hash_function=DEFAULT_HASH)
        
        or
        
        key_deriver = hkdf.HKDF(hash_function=DEFAULT_HASH)
        key_deriver.hkdf(input_keying_material, length, info='', salt='')
         
    From http://tools.ietf.org/html/rfc5869 :
        
        A key derivation function (KDF) is a basic and essential component of
        cryptographic systems.  Its goal is to take some source of initial
        keying material and derive from it one or more cryptographically
        strong secret keys."""
import math
import hashlib
import hmac
import six

#from cryptography.hazmat.primitives.hmac import HMAC
#from cryptography.hazmat.primitives import hashes
#from security import BACKEND

DEFAULT_HASH = "sha256"
OUTPUT_SIZES = {"sha1" : 20,
                "sha224" : 28,
                "sha256" : 32,
                "sha384" : 48,
                "sha512" : 64}
                    
def extract(input_keying_material, salt, hash_function=DEFAULT_HASH):
    hasher = getattr(hashlib, hash_function.lower())
    return hasher(salt + bytes(input_keying_material)).digest()    
    
def expand(psuedorandom_key, length=32, info='', hash_function=DEFAULT_HASH):
    outputs = [b'']
    hasher = getattr(hashlib, hash_function)
    blocks, extra = divmod(length, hasher().digest_size)
    blocks += 1 if extra else 0
    for counter in range(blocks):
        outputs.append(hmac.HMAC(psuedorandom_key, 
                                 outputs[-1] + info + six.int2byte(counter), 
                                 hasher).digest())      
    return b''.join(outputs)[:length]
    
def hkdf(input_keying_material, length, info='', salt='', hash_function=DEFAULT_HASH):
    return expand(extract(input_keying_material, salt), 
                  length, info, hash_function)
    
class HKDF(object):
                        
    def __init__(self, hash_function=DEFAULT_HASH):
        self.hash_function = hash_function
        self.hash_length = OUTPUT_SIZES[hash_function]
        
    def extract(self, input_keying_material, salt=''):
        return extract(input_keying_material, salt, self.hash_function)        
        
    def expand(self, psuedorandom_key, length, info=''):
        return expand(psuedorandom_key, length=length, info=info, hash_function=self.hash_function)
        
    def hkdf(self, input_keying_material, length, info='', salt=''):
        return hkdf(input_keying_material, length, info, salt)
        
        
if __name__ == "__main__":
    print expand("testing", info="testing")