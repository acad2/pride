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

DEFAULT_HASH = hashlib.sha256
OUTPUT_SIZES = {hashlib.sha1 : 20,
                hashlib.sha224 : 28,
                hashlib.sha256 : 32,
                hashlib.sha384 : 48,
                hashlib.sha512 : 64}
                    
def extract(input_keying_material, salt, hash_function=DEFAULT_HASH):
    psuedorandom_key = hash_function(salt + input_keying_material).digest()
    return psuedorandom_key
    
def expand(psuedorandom_key, length, hash_length,
           info='', hash_function=DEFAULT_HASH):
    n = int(math.ceil(length / hash_length))
    t = r''
    for counter in xrange(n):
        t += hash_function(psuedorandom_key + t + info + hex(counter)).digest()
    output_keying_material = t[:length]
    return output_keying_material
    
def hkdf(input_keying_material, length, info='', salt='', hash_function=DEFAULT_HASH):
    return expand(extract(input_keying_material, salt), 
                  length, 
                  OUTPUT_SIZES[hash_function],
                  info,
                  hash_function)
    
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
            t += self.hash_function(psuedorandom_key + t + info + hex(counter)).digest()
        output_keying_material = t[:length]
        return output_keying_material
        
    def hkdf(self, input_keying_material, length, info='', salt=''):
        return self.expand(self.extract(input_keying_material, salt), length, info)
        
if __name__ == "__main__":
    print hkdf("test input keying material", 32, info="application info", salt='salt')
    deriver = HKDF(hashlib.sha256)
    print deriver.hkdf("test input keying material", 32, info="application info", salt="salt")