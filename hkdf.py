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

DEFAULT_HASH = hashlib.sha256
OUTPUT_SIZES = {hashlib.sha1 : 20,
                hashlib.sha224 : 28,
                hashlib.sha256 : 32,
                hashlib.sha384 : 48,
                hashlib.sha512 : 64}
                    
def extract(input_keying_material, salt, hash_function=DEFAULT_HASH):
    return hash_function(salt + bytes(input_keying_material)).digest()    
    
def expand(psuedorandom_key, length=32, info='', hash_function=DEFAULT_HASH):
    outputs = [b'']
    for counter in xrange(1, 1 + int(math.ceil(length / hash_function().digest_size))):
        outputs.append(hmac.HMAC(psuedorandom_key, 
                                 outputs[-1] + info + six.int2byte(counter), 
                                 hash_function).digest())    
    return b''.join(outputs)[:length]
    
def hkdf(input_keying_material, length, info='', salt='', hash_function=DEFAULT_HASH):
    return expand(extract(input_keying_material, salt), 
                  length, info, hash_function)
    
class HKDF(object):
                        
    def __init__(self, hash_function=DEFAULT_HASH):
        self.hash_function = hash_function
        self.hash_length = OUTPUT_SIZES[hash_function]
        
    def extract(self, input_keying_material, salt=''):
        psuedorandom_key = self.hash_function(salt + input_keying_material).digest()
        return psuedorandom_key
        
    def expand(self, psuedorandom_key, length, info=''):
        n = int(math.ceil(length / self.hash_length))
        t = r''
        for counter in xrange(n):
            t += self.hash_function(psuedorandom_key + t + info + six.int2byte(counter)).digest()
        output_keying_material = t[:length]
        return output_keying_material
        
    def hkdf(self, input_keying_material, length, info='', salt=''):
        return self.expand(self.extract(input_keying_material, salt), length, info)
        
if __name__ == "__main__":
    print expand("testing", info="testing")