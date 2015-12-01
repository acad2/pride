import random

import pride.base

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
crypto_backend = default_backend()

class User(pride.base.Base):
    
    defaults = {"hash_function" : "SHA256", "mac_key" : None,
                "encryption_key" : None, "salt" : None, "salt_size" : 16,
                "key_length" : 32, "kdf_iteration_count" : 100000,
                "password" : '', "username" : '',
                "crypto_backend" : "cryptography.hazmat.backends.default_backend",
                "master_key_derivation_function" : 
                 "cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC",
                 "hkdf_mac_info_string" : "{} Message Authentication Code Key"}
    
    def _get_password(self):
        return self._password or getpass.getpass(self.password_prompt)
    def _set_password(self, value):
        self._password = value
    password = property(_get_password, _set_password)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        name = self.instance_name.replace("->", '_')
        with open("{}_salt.bin", "a+b") as _file:
            _file.seek(0)
            self.salt = salt = _file.read()
            if not salt:
                salt = random._urandom(self.salt_size)
                _file.write(salt)
        hash_algorithm = getattr(hashes, self.hash_function)
        key_length = self.key_length
        kdf = self.create(self.master_key_derivation_function,
                          algorithm=hash_algorithm,
                          length=key_length, salt=salt,
                          iterations=self.kdf_iteration_count,
                          backend=self.create(self.crypto_backend))
        master_key = kdf.derive(self.password)
        
        hkdf_options = {"algorithm" : hash_algorithm, "length" : key_length,
                        "info" : self.hkdf_mac_info_string.format(self.username + salt),
                        "backend" : crypto_backend}
                        
        mac_kdf = self.create("cryptography.hazmat.primitives.kdf.hkdf.HKDFExpand",
                              **hkdf_options)
        mac_key = self.mac_key = hkdf.derive(master_key)
        
        hkdf_options["info"] = self.hkdf_encryption_info_string.format(self.username + salt)
        encryption_kdf = self.create("cryptography.hazmat.primitives.kdf.hkdf.HKDFExpand",
                                     **hkdf_options)
        encryption_key = self.encryption_key = encryption_hkdf.derive(master_key)
        
        
    def apply_mac(self, data):
        return hmac.new(self.mac_key, data, 
                        getattr(hashlib, self.hash_function)).digest()  
                        
    def verify_mac(self, mac, data):
        return hmac.compare_digests(mac, hmac.new(self.mac_key, data,
                                                  getattr(hashlib, self.hash_function)).digest())
                                                  
    def encrypt(self, data):
        raise NotImplementedError