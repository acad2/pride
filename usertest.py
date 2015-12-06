import getpass
import random

import pride.base
import pride.security

class User(pride.base.Base):
    
    defaults = {"hash_function" : "SHA256", "mac_key" : None,
                "encryption_key" : None, "salt" : None, "salt_size" : 16,
                "key_length" : 32, "kdf_iteration_count" : 100000, 
                "encryption_mode" : "GCM", "password" : '', "username" : '', 
                "encryption_algorithm" : "AES",
                "hkdf_mac_info_string" : "{} Message Authentication Code Key",
                "hkdf_encryption_info_string" : "{} Encryption Key",
                "password_prompt" : "{}: Please provide the pass phrase or word: "}
    
    parser_ignore = ("mac_key", "encryption_key", "hkdf_mac_info_string", 
                     "hkdf_encryption_info_string", "password_prompt")
    
    flags = {"_password_verifier_size" : 32}.items()
    
    def _get_password(self):
        return self._password or getpass.getpass(self.password_prompt.format(self.instance_name))
    def _set_password(self, value):
        self._password = value
    password = property(_get_password, _set_password)
    
    def _get_username(self):
        if not self._username:
            username_prompt = "{}: please provide a username: ".format(self.instance_name)
            self._username = pride.shell.get_user_input(username_prompt)
        return self._username
    def _set_username(self, value):
        self._username = value
    username = property(_get_username, _set_username)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        login_success = False
        while not login_success:
            try:
                self.login()
            except pride.security.InvalidPassword:
                continue
            else:
                login_success = True
        
    def login(self):
        if not self.salt:
            with open("{}_salt.bin".format(self.username), "a+b") as _file:
                _file.seek(0)
                salt = _file.read(self.salt_size)
                if not salt:
                    salt = random._urandom(self.salt_size)
                    _file.write(salt)
        else:
            salt = self.salt            
        key_length = self.key_length
        kdf = self.create("pride.security.key_derivation_function", 
                          algorithm=self.hash_function, length=key_length, 
                          salt=salt, iterations=self.kdf_iteration_count)
        master_key = kdf.derive(self.password)
        
        hkdf_options = {"algorithm" : self.hash_function, "length" : key_length,
                        "info" : self.hkdf_encryption_info_string.format(self.username + salt)}      
        
        encryption_kdf = self.create("pride.security.hkdf_expand", **hkdf_options)
        encryption_key = encryption_kdf.derive(master_key)
        
        with open("{}_password_verifier.bin".format(self.username), "a+b") as _file:
            verifier_size = self._password_verifier_size
            salt_size = self.salt_size
            verifier = _file.read(verifier_size + salt_size * 3)
            if not verifier:
                verifier = random._urandom(verifier_size)
                ciphertext, iv, tag = self.encrypt(verifier)
                _file.seek(0)
                _file.write(ciphertext + iv + tag)
            else:                
                ciphertext = verifier[:verifier_size]
                iv = verifier[verifier_size:verifier_size + salt_size]
                tag = verifier[verifier_size + salt_size:verifier_size + (salt_size * 2)]
            try:
                self.decrypt(ciphertext, iv, tag)
            except pride.security.InvalidTag:
                self.alert("Password failed to match password verifier", level=0)
                raise pride.security.InvalidPassword()
       
        hkdf_options["info"] = self.hkdf_mac_info_string.format(self.username + salt)        
        mac_kdf = self.create("pride.security.hkdf_expand", **hkdf_options)
        self.mac_key = mac_kdf.derive(master_key)
        self.encryption_key = encryption_key
        self.salt = salt
        
    def encrypt(self, data, extra_data=''):
        return pride.security.encrypt(data=data, key=self.encryption_key, iv=random._urandom(16),
                                      extra_data=extra_data, algorithm=self.encryption_algorithm, 
                                      mode=self.encryption_mode)
                                      
    def decrypt(self, ciphertext, iv, tag=None, extra_data=''):
        return pride.security.decrypt(ciphertext, self.encryption_key, iv, tag, extra_data,
                                      self.encryption_algorithm, self.encryption_mode)
    
    def authenticate(self, data):
        return pride.security.apply_mac(self.mac_key, data, self.hash_function)
        
    def verify(self, mac, data):
        return pride.security.verify_mac(self.mac_key, data, mac, self.hash_function)
        
    def reset_environment(self):
        environment = pride.environment
        for field in pride.environment.fields:
            setattr(environment, field, [])
        environment.Instructions = []
        environment.last_creator = None
        
def test_User():
    user = User()
    data = "This is some test data!"
    ciphertext, iv, tag  = user.encrypt(data)
    assert user.decrypt(ciphertext, iv, tag=tag) == data
    
if __name__ == "__main__":
    test_User()
    