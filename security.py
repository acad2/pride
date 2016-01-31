""" Provides security related functions such as encryption and decryption.
    Two backends are available: Ideally, the cryptography package has been
    installed, and that will be used. In situations where that is not feasible,
    usually due to permissions, the pride.cryptographyless module will be used
    instead. """
import os

class SecurityError(Exception): pass
class InvalidPassword(SecurityError): pass

def random_bytes(count):
    """ Generates count cryptographically secure random bytes """
    return os.urandom(count)

def pack_data(*args): # copied from pride.utilities
    """ Pack arguments into a stream, prefixed by size headers.
        Resulting bytestream takes the form:
            
            size1 size2 size3 ... sizeN data1data2data3...dataN
            
        The returned bytestream can be unpacked via unpack_data to
        return the original contents, in order. """
    sizes = []
    for arg in args:
        sizes.append(str(len(arg)))
    return ' '.join(sizes + [args[0]]) + ''.join(str(arg) for arg in args[1:])
    
def unpack_data(packed_bytes, size_count):
    """ Unpack a stream according to its size header """
    sizes = packed_bytes.split(' ', size_count)
    packed_bytes = sizes.pop(-1)
    data = []
    for size in (int(size) for size in sizes):
        data.append(packed_bytes[:size])
        packed_bytes = packed_bytes[size:]
    return data
    
    
try:
    import cryptography
   # raise ImportError
except ImportError:
    # use an alternative file when the cryptography package is not installed
    import hashlib
    
    import cryptographyless
    import hkdf
    
    class InvalidSignature(SecurityError): pass
    class InvalidTag(SecurityError): pass

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
        return hmac.HMAC(key, data, hash_function(algorithm)).digest()
        
    def apply_mac(key, data, algorithm="SHA256", backend=None):
        return pack_data(generate_mac(key, data, algorithm, backend), data)
                        
    def verify_mac(key, packed_data, algorithm="SHA256", backend=None):
        """ Verifies a message authentication code as obtained by apply_mac.
            Successful comparison indicates integrity and authenticity of the data. """
        mac, data = unpack_data(packed_data, 2)
        calculated_mac = hmac.HMAC(key, data, hash_function(algorithm)).digest()        
        try:
            if not hmac.HMAC.compare_digest(mac, calculated_mac):
                raise InvalidTag()
        except InvalidTag: # to be consistent with how it is done when the cryptography package is used
            return False
        else:
            return True    

    def encrypt(data='', key='', iv=None, extra_data='', algorithm="sha512",
                mode=None, backend=None, iv_size=16):        
        iv = iv or random_bytes(iv_size)        
        return cryptographyless.encrypt(data, key, iv, extra_data)      
        
    def decrypt(packed_encrypted_data, key, algorithm="sha512",
                mode=None, backend=None):
        """ Decrypts packed encrypted data as returned by encrypt with the same key. 
            If extra data is present, returns plaintext, extra_data. If not,
            returns plaintext. Raises InvalidTag on authentication failure. """
        return cryptographyless.decrypt(packed_encrypted_data, key)
        
else:
    del cryptography    
    from cryptography.exceptions import InvalidTag, InvalidSignature
    from cryptography.hazmat.primitives.hmac import HMAC
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF, HKDFExpand
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import openssl
    BACKEND = openssl.backend      
        
    def hash_function(algorithm_name, backend=BACKEND):
        """ Returns a Hash object of type algorithm_name from 
            cryptography.hazmat.primitives.hashes """
        return hashes.Hash(getattr(hashes, algorithm_name)(), backend=backend)
        
    def key_derivation_function(salt, algorithm="SHA256", length=32, 
                                iterations=100000, backend=BACKEND):
        """ Returns an key derivation function object from
            cryptography.hazmat.primitives.kdf.pbkdf2 """
        return PBKDF2HMAC(algorithm=getattr(hashes, algorithm)(),
                          length=length, salt=salt, iterations=iterations,
                          backend=backend)
        
    def hkdf_expand(algorithm="SHA256", length=256, info='', backend=BACKEND):
        """ Returns an hmac based key derivation function (expand only) from
            cryptography.hazmat.primitives.hkdf. """
        return HKDFExpand(algorithm=getattr(hashes, algorithm)(),
                          length=length, info=info, backend=BACKEND)
    
    def apply_mac(key, data, algorithm="SHA256", backend=BACKEND):
        """ Generates a message authentication code and prepends it to data.
            Mac and data are packed via pride.utilities.pack_data. 
            
            Applying a message authentication code facilitates the goals
            of authenticity and integrity. Note it does not protect
            confidentiality (i.e. encryption).
            
            Combining a mac with encryption is NOT straightforward;
            Authenticating/providing integrity of confidential data
            should preferably be accomplished via an appropriate
            block cipher mode of operation, such as GCM. If this is
            not possible, encrypt-then-mac is most secure solution in
            general. """
        return pack_data(generate_mac(key, data, algorithm, backend), data)
                
    def generate_mac(key, data, algorithm="SHA256", backend=BACKEND):
        """ Returns a message authentication code for verifying the integrity and
            authenticity of data by entities that possess the key. 
            
            Note this is a lower level function then apply_mac and
            only returns the mac itself. 
            
            The mac is generated via HMAC with the specified algorithm and key. """
        hasher = HMAC(key, getattr(hashes, algorithm)(), backend=backend)
        hasher.update(data)
        return hasher.finalize()
                        
    def verify_mac(key, packed_data, algorithm="SHA256", backend=BACKEND):
        """ Verifies a message authentication code as obtained by apply_mac.
            Successful comparison indicates integrity and authenticity of the data. """
        mac, data = unpack_data(packed_data, 2)
        hasher = HMAC(key, getattr(hashes, algorithm)(), backend=backend)
        hasher.update(data)
        try:
            hasher.verify(mac)
        except InvalidSignature:
            return False
        else:
            return True
                                
    def encrypt(data='', key='', iv=None, extra_data='', algorithm="AES",
                mode="GCM", backend=BACKEND, iv_size=16, mac_key=''):
        """ Encrypts data with the specified key. Returns packed encrypted bytes.
            If an iv is not supplied a random one of iv_size will be generated.
            By default, the GCM mode of operation is used and the iv is 
            automatically included in the extra_data authenticated by the mode. """
        assert data and key
        iv = iv or random_bytes(iv_size)
        encryptor = Cipher(getattr(algorithms, algorithm)(key), 
                        getattr(modes, mode)(iv), 
                        backend=BACKEND).encryptor()
        if mode == "GCM":        
            encryptor.authenticate_additional_data(extra_data)            
        ciphertext = encryptor.update(data) + encryptor.finalize()  
        header = algorithm + '_' + mode
        try:
            return pack_data(header, ciphertext, iv, encryptor.tag, extra_data)
        except AttributeError:
            return pack_data(header, ciphertext, iv, '', '')
        
    def decrypt(packed_encrypted_data, key, backend=BACKEND):
        """ Decrypts packed encrypted data as returned by encrypt with the same key. 
            If extra data is present, returns plaintext, extra_data. If not,
            returns plaintext. Raises InvalidTag on authentication failure. """
        header, ciphertext, iv, tag, extra_data = unpack_data(packed_encrypted_data, 5)        
        algorithm, mode = header.split('_', 1)
        if mode == "GCM" and not tag:
            raise ValueError("Tag not supplied for GCM mode")
        mode_args = (iv, tag) if mode == "GCM" else (iv, )
        decryptor = Cipher(getattr(algorithms, algorithm)(key), 
                           getattr(modes, mode)(*mode_args), 
                           backend=BACKEND).decryptor()
        if mode == "GCM":
            decryptor.authenticate_additional_data(extra_data)
        if extra_data:
            return (decryptor.update(ciphertext) + decryptor.finalize(), extra_data)     
        else:
            return decryptor.update(ciphertext) + decryptor.finalize()      
            
def test_packed_encrypted_data():
    data = "This is some fantastic test data"
    key = random_bytes(32)
    packed_encrypted_data = encrypt(data, key)
    plaintext = decrypt(packed_encrypted_data, key)
    assert plaintext == data
    
if __name__ == "__main__":
    test_packed_encrypted_data()