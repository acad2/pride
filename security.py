""" Provides security related functions such as encryption and decryption.
    Two backends are available: Ideally, the cryptography package has been
    installed, and that will be used. In situations where that is not feasible,
    usually due to permissions, the pride.cryptographyless module will be used
    instead. """
import os

from pride.utilities import pack_data, unpack_data

class SecurityError(Exception): pass
class InvalidPassword(SecurityError): pass

def random_bytes(count):
    """ Generates count cryptographically secure random bytes """
    return os.urandom(count) 
    
try:
    import cryptography
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
        mac, data = unpack_data(packed_data)
        calculated_mac = hmac.HMAC(key, data, hash_function(algorithm)).digest()        
        try:
            if not hmac.HMAC.compare_digest(mac, calculated_mac):
                raise InvalidTag()
        except InvalidTag: # to be consistent with how it is done when the cryptography package is used
            return False
        else:
            return True    

    def encrypt(data='', key='', iv=None, extra_data='', algorithm="sha512",
                mode=None, backend=None, iv_size=16, mac_key=None):        
        iv = iv or random_bytes(iv_size)        
        return cryptographyless.encrypt(data, key, iv, extra_data)      
        
    def decrypt(packed_encrypted_data, key, algorithm="sha512",
                mode=None, backend=None, mac_key=None):
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
        mac, data = unpack_data(packed_data)
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
            automatically included in the extra_data authenticated by the mode. 
            
            Note that not all algorithms may support all modes of operation
            with all backends. 
            
            A mac key is required when GCM mode is not in used. This function
            will refuse to encrypt data without authentication/integrity checks,
            as this is considered a serious flaw in security. 
            
            Technically speaking, 'iv' is not always the correct term for the
            parameter passed, depending on the mode of operation used. However,
            using two different fields for what are functionally the same would
            increase complexity needlessly. """
        assert data and key
        header = algorithm + '_' + mode   
        if mode != "GCM" and not mac_key:
            raise ValueError("Unable to authenticate data because no mac key was supplied for {} mode".format(header))        
        if not iv and iv != 0: # 0 is a valid nonce for CTR mode.
            iv = random_bytes(iv_size)
        encryptor = Cipher(getattr(algorithms, algorithm)(key), 
                           getattr(modes, mode)(iv), 
                           backend=BACKEND).encryptor()
        if mode == "GCM":        
            encryptor.authenticate_additional_data(extra_data)            
        ciphertext = encryptor.update(data) + encryptor.finalize()          
                     
        if mode == "GCM":
            mac_tag = encryptor.tag
        else:
            mac_tag = generate_mac(mac_key, header + ciphertext + iv + extra_data)        
        return pack_data(header, ciphertext, iv, mac_tag, extra_data)
        
    def decrypt(packed_encrypted_data, key, mac_key='', backend=BACKEND):
        """ Decrypts packed encrypted data as returned by encrypt with the same key. 
            If extra data is present, returns plaintext, extra_data. If not,
            returns plaintext. Raises InvalidTag on authentication failure. """
        header, ciphertext, iv, tag, extra_data = unpack_data(packed_encrypted_data)        
        algorithm, mode = header.split('_', 1)        
        mode_args = (iv, tag) if mode == "GCM" else (iv, )
        decryptor = Cipher(getattr(algorithms, algorithm)(key), 
                           getattr(modes, mode)(*mode_args), 
                           backend=BACKEND).decryptor()
        if mode == "GCM":
            decryptor.authenticate_additional_data(extra_data)
        elif not verify_mac(mac_key, pack_data(tag, header + ciphertext + iv + extra_data)):
            raise InvalidTag("Failed to authenticate data")
            
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        if extra_data:
            return (plaintext, extra_data)     
        else:
            return plaintext
            
def test_packed_encrypted_data():
    data = "This is some fantastic test data"
    key = random_bytes(32)
    mac_key = random_bytes(16)
    for algorithm in ("AES", "Camellia"):
        for mode in ("CBC", "CTR", "GCM"):
            if algorithm == "Camellia" and mode in ("GCM", "CTR"): 
                continue
            packed_encrypted_data = encrypt(data, key, algorithm=algorithm, mode=mode, 
                                            mac_key=mac_key)                        
            plaintext = decrypt(packed_encrypted_data, key, mac_key=mac_key)            
            assert plaintext == data
    
if __name__ == "__main__":
    test_packed_encrypted_data()