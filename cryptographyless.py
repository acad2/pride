""" Provides authenticated encryption and decryption functions using only the python standard library.
    To be used in situations where the cryptography module cannot be installed, usually for permission reasons. """
    
import itertools
import hashlib
import hmac
import os

from pride.utilities import save_data, load_data
from pride.errors import InvalidTag
from pride import hkdf

__all__ = ("InvalidTag", "random_bytes", "psuedorandom_bytes", "encrypt", "decrypt", 
           "Hash_Object", "Key_Derivation_Object", "HKDFExpand", "hkdf_expand",
           "key_derivation_function", "generate_mac", "apply_mac", "verify_mac",
           "hash_function")

_TEST_KEY = "\x00" * 16
_TEST_MESSAGE = "This is a sweet test message :)"

def random_bytes(count):
    """ Generates count cryptographically secure random bytes """
    return os.urandom(count) 
    
class Hash_Object(object):
    
    def __init__(self, algorithm="md5"):
        self.hash_object = getattr(hashlib, algorithm.lower())()
        
    def __getattr__(self, attribute):
        try:
            return getattr(super(Hash_Object, self).__getattribute__("hash_object"), attribute)
        except AttributeError:
            if attribute == "finalize":
                return super(Hash_Object, self).__getattribute__("finalize")
            else:
                raise
                
    def finalize(self):
        return self.hash_object.digest()
        
    
class Key_Derivation_Object(object):
    
    def __init__(self, algorithm, length, salt, iterations):
        self.algorithm = algorithm
        self.length = length
        self.salt = salt
        self.iterations = iterations
        
    def derive(self, kdf_input):
        return hashlib.pbkdf2_hmac(self.algorithm, kdf_input, self.salt, 
                                   self.iterations, self.length)
        
class HKDFExpand(object):
    
    def __init__(self, algorithm="sha256", length=32, info='', backend=None):
        self.algorithm = algorithm
        self.length = length
        self.info = info
        
    def derive(self, key_material):
        return hkdf.expand(key_material, length=self.length, info=self.info, 
                           hash_function=getattr(hashlib, self.algorithm.lower()))
                           
        
def hash_function(algorithm_name, backend=None):
    return Hash_Object(algorithm_name.lower())#getattr(hashlib, algorithm_name.lower())()
 
def hkdf_expand(algorithm="SHA256", length=256, info='', backend=None):
    """ Returns an hmac based key derivation function (expand only) from
        cryptography.hazmat.primitives.hkdf. """
    return HKDFExpand(algorithm, length, info, backend)
                      
def key_derivation_function(salt, algorithm="sha256", length=32, 
                            iterations=100000, backend=None):
    return Key_Derivation_Object(algorithm, length, salt, iterations)
    
def generate_mac(key, data, algorithm="SHA256", backend=None):
    return hmac.HMAC(key, algorithm + "::" + data, hash_function(algorithm)).digest()
    
def apply_mac(key, data, algorithm="SHA256", backend=None):
    return save_data(generate_mac(key, data, algorithm, backend), data)
                    
def verify_mac(key, packed_data, algorithm="SHA256", backend=None):
    """ Verifies a message authentication code as obtained by apply_mac.
        Successful comparison indicates integrity and authenticity of the data. """
    mac, data = load_data(packed_data)
    calculated_mac = hmac.HMAC(key, algorithm + "::" + data, hash_function(algorithm)).digest()        
    try:
        if not hmac.HMAC.compare_digest(mac, calculated_mac):
            raise InvalidTag()
    except InvalidTag: # to be consistent with how it is done when the cryptography package is used
        return False
    else:
        return True    

def encrypt(data='', key='', mac_key=None,iv=None, extra_data='', algorithm="SHA256",
            mode=None, backend=None, iv_size=16, hash_algorithm="sha256"):        
    iv = iv or random_bytes(iv_size)
    if (not data) or (not key) or (not mac_key):
        raise ValueError("Encryption requires data, encryption key, and mac key")
    return _encrypt(data, key, mac_key, iv, extra_data)      
            
def decrypt(packed_encrypted_data, key, mac_key, backend=None):
    """ Decrypts packed encrypted data as returned by encrypt with the same key. 
        If extra data is present, returns plaintext, extra_data. If not,
        returns plaintext. Raises InvalidTag on authentication failure. """       
    return _decrypt(packed_encrypted_data, key, mac_key)        
    
def _hmac_rng(key, seed, hash_function="SHA256"):
    """ Generates psuedorandom bytes via HMAC. Implementation could be improved to
        a compliant scheme like HMAC-DRBG. """
    hasher = hmac.HMAC(key, seed, getattr(hashlib, hash_function.lower()))
    for counter in (str(number) for number in itertools.count()):
        yield hasher.digest()
        hasher.update(key + seed + counter)
    
def psuedorandom_bytes(key, seed, count, hash_function="SHA256"): 
    """ usage: psuedorandom_bytes(key, seed, count, 
                                  hash_function="SHA256") => psuedorandom bytes
                
        Generates count cryptographically secure psuedorandom bytes. 
        Bytes are produced deterministically based on key and seed, using 
        hash_function with _hmac_rng. """
    hash_function = hash_function.lower()
    generator = _hmac_rng(key, seed, hash_function)
    output = ''
    output_size = getattr(hashlib, hash_function)().digest_size    
    iterations, extra = divmod(count, output_size)
    for round in range(iterations + 1 if extra else iterations):
        output += next(generator)
    return output[:count]       
            
def _hash_stream_cipher(data, key, nonce, hash_function="SHA256"):    
    """ Generates key material and XORs with data. Provides confidentiality,
        but not authenticity or integrity. As such, this should seldom be used alone. """    
    output = bytearray(data)
    for index, key_byte in enumerate(bytearray(psuedorandom_bytes(key, nonce, len(data), hash_function))):
        output[index] ^= key_byte
    return bytes(output)    
        
def _encrypt(data, key, mac_key, nonce='', extra_data='', hash_function="SHA256", nonce_size=32):
    """ usage: _encrypt(data, key, extra_data='', nonce='', 
                hash_function="SHA256", nonce_size=32) => encrypted_packet
    
        Encrypts data using key. 
        Returns a packet of encrypted data, nonce, mac_tag, extra_data
        Authentication and integrity of data, nonce, and extra data are assured
        Confidentiality of data is assured.
        
        Encryption is provided by _hash_stream_cipher.
        Integrity/authenticity are provided via HMAC. 
        nonce is randomly generated when not supplied (recommended)
        nonce_size defaults to 32; decreasing below 16 may destroy security"""    
    nonce = nonce or os.urandom(nonce_size)
    hash_function = hash_function.upper()
    encrypted_data = _hash_stream_cipher(data, key, nonce, hash_function)
    header = hash_function + '_' + hash_function + "_" + hash_function
    mac_tag = hmac.HMAC(mac_key, header + extra_data + nonce + encrypted_data, getattr(hashlib, hash_function.lower())).digest()
    return save_data(header, encrypted_data, nonce, mac_tag, extra_data)
        
def _decrypt(data, key, mac_key, hash_function="SHA256"):
    """ usage: _decrypt(data, key, mac_key,
                        hash_function) => (plaintext, extra_data)
                                           or
                                           plaintext
                                          
        Returns (extra_data, plaintext) when extra data is available
        Otherwise, just returns plaintext data. 
        Authenticity and integrity of the plaintext/extra data is guaranteed. """
    header, encrypted_data, nonce, mac_tag, extra_data = load_data(data)
    hash_function, _, hash_function = header.split('_', 2)
    hash_function = hash_function.lower()
    try:
        hasher = getattr(hashlib, hash_function)
    except AttributeError:
        raise ValueError("Unsupported mode {}".format(header))
        
    if hmac.HMAC(mac_key, header + extra_data + nonce + encrypted_data, hasher).digest() == mac_tag:
        plaintext = _hash_stream_cipher(encrypted_data, key, nonce, hash_function)
        if extra_data:
            return (plaintext, extra_data)
        else:
            return plaintext
    else:
        raise InvalidTag("Invalid tag")
        
def test_hmac_rng():
    output = ''
    one_megabyte = 1024 * 1024
    for random_data in _hmac_rng(_TEST_KEY, _TEST_MESSAGE):
        output += random_data
        if len(output) >= one_megabyte: 
            break
    
    outputs = dict((x, output.count(chr(x))) for x in xrange(256))
    import pprint
    #pprint.pprint(sorted(outputs.items()))
    
    output2 = psuedorandom_bytes(_TEST_KEY, _TEST_MESSAGE, one_megabyte)
    assert output == output2, (len(output), len(output2))
    
def test__encrypt__decrypt():        
    packet = _encrypt(_TEST_MESSAGE, _TEST_KEY, _TEST_KEY, extra_data="extra_data")
    #print "Encrypted packet: \n\n\n", packet
    decrypted = _decrypt(packet, _TEST_KEY, _TEST_KEY)
    assert decrypted == (_TEST_MESSAGE, "extra_data"), decrypted
    
    header, encrypted_data, nonce, mac_tag, extra_data = load_data(packet)
    extra_data = "Changed"
    packet = save_data(header, encrypted_data, nonce, mac_tag, extra_data)
    try:
        _decrypt(packet, _TEST_KEY, _TEST_KEY)
    except InvalidTag:
        pass
    else:
        print "Failed to protect authenticity/integrity of extra_data"
        assert False
    
def test_encrypt_decrypt():
    packet = encrypt(_TEST_MESSAGE, _TEST_KEY, _TEST_KEY, extra_data="extra data")
    decrypted = decrypt(packet, _TEST_KEY, _TEST_KEY)
    assert decrypted == (_TEST_MESSAGE, "extra data"), decrypted
        
if __name__ == "__main__":
    test_hmac_rng()
    test__encrypt__decrypt()
    test_encrypt_decrypt()