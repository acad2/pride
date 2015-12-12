import getpass
import random

import pride.base
import pride.security

class User(pride.base.Base):
    """ A User object for managing secure information and client accounts.
        A user is capable of performing manipulation of secure data,
        including encryption and decryption. The user object is responsible
        for deriving and holding keys required for such manipulation. """
    defaults = {# encryption configuration options    
                # these may need to update with time
                "hash_function" : "SHA256", "kdf_iteration_count" : 100000, 
                "salt_size" : 16, "key_length" : 32, "iv_size" : 16,
                
                # these will probably be updated less frequently
                "encryption_mode" : "GCM", "encryption_algorithm" : "AES",
                
                # login/key derivation can be bypassed by supplying keys directly
                # note that encryption key, salt, and mac key must be supplied to
                # skip the login/key derivation process. This is not recommended!
                "encryption_key" : None, "salt" : None, "mac_key" : None,
                
                # similarly, username and password may be assigned instead of prompted. 
                # Not recommended!
                "password" : '', "username" : '', 
                
                # These may be changed for specific application needs
                "hkdf_mac_info_string" : "{} Message Authentication Code Key",
                "hkdf_encryption_info_string" : "{} Encryption Key",
                "password_prompt" : "{}: Please provide the pass phrase or word: ",
                "salt_filetype" : "pride.fileio.Database_File",
                "verifier_filetype" : "pride.fileio.Database_File"}
    
    parser_ignore = ("mac_key", "encryption_key", "hkdf_mac_info_string", 
                     "hkdf_encryption_info_string", "password_prompt")
    
    flags = {"_password_verifier_size" : 32}.items()
    
    verbosity = {"password_verified" : 'v'}
    
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
        login_success = self.encryption_key and self.mac_key and self.salt
        while not login_success:
            try:
                self.login()
            except pride.security.InvalidPassword:
                self.username = self.password = None
                continue
            else:
                login_success = True
        
    def login(self):
        """ Attempt to login as username using a password. Upon success, the
            users encryption and mac key are derived and stored in memory.
            Upon failure, the prompt is repeated. """
        if not self.salt:
            with self.create(self.salt_filetype, # uses Database_Files by default
                             "{}_salt.bin".format(self.username), 
                             "a+b") as _file:
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
        master_key = kdf.derive(self.username + ':' + self.password)
        
        hkdf_options = {"algorithm" : self.hash_function, "length" : key_length,
                        "info" : self.hkdf_encryption_info_string.format(self.username + salt)}      
        
        encryption_kdf = self.create("pride.security.hkdf_expand", **hkdf_options)
        encryption_key = self.encryption_key = encryption_kdf.derive(master_key)
        
        with self.create(self.verifier_filetype,
                         "{}_password_verifier.bin".format(self.username), 
                         "a+b") as _file:
            verifier_size = self._password_verifier_size
            salt_size = self.salt_size
            verifier = _file.read()
            if not verifier:
                verifier = random._urandom(verifier_size)
                encrypted_verifier = self.encrypt(verifier)
                _file.seek(0)
                _file.write(str(len(encrypted_verifier)) + ' ' + encrypted_verifier)
            else:
                size, _verifier = verifier.split(' ', 1)
                encrypted_verifier = _verifier[:int(size)]
            try:
                self.decrypt(encrypted_verifier)
            except pride.security.InvalidTag:
                self.alert("Password failed to match password verifier", level=0)
                self.encryption_key = None
                raise pride.security.InvalidPassword()
            else:
                self.alert("Password verified", level=self.verbosity["password_verified"])
        hkdf_options["info"] = self.hkdf_mac_info_string.format(self.username + salt)        
        mac_kdf = self.create("pride.security.hkdf_expand", **hkdf_options)
        self.mac_key = mac_kdf.derive(master_key)
        self.encryption_key = encryption_key
        self.salt = salt
        
    def encrypt(self, data, extra_data=''):
        """ Encrypt and authenticates the supplied data and authenticates, but 
            does not encrypt, any extra_data. The data is encrypted using the 
            Users encryption key. Returns packed encrypted bytes. """
        return pride.security.encrypt(data=data, key=self.encryption_key, iv=random._urandom(self.iv_size),
                                      extra_data=extra_data, algorithm=self.encryption_algorithm, 
                                      mode=self.encryption_mode)
                                      
    def decrypt(self, packed_encrypted_data):
        """ Decrypts packed encrypted data as returned by encrypt. The Users 
            encryption key is used to decrypt the data. """
        return pride.security.decrypt(packed_encrypted_data, self.encryption_key, 
                                      self.encryption_algorithm, self.encryption_mode)
    
    def authenticate(self, data):
        """ Authenticates and provides integrity to a piece of data. 
            Authentication and integrity are generally requirements for any data
            that must be secured. Returns a message authentication code.
            
            Note that User.encrypt uses AES-GCM mode, which authenticates
            data and extra_data automatically. 
            
            Combining encryption and authentication is not simple. This method 
            should be used ONLY in conjunction with unencrypted data, unless 
            you are certain you know what you are doing. """
        return pride.security.apply_mac(self.mac_key, data, self.hash_function)
        
    def verify(self, mac, data):
        """ Verifies data with the mac returned by authenticate. Data that is 
            verified has two extremely probable guarantees: that it did indeed
            come from who it was supposed to have come from, and that it was
            not manipulated by unauthorized parties in transit. """
        return pride.security.verify_mac(self.mac_key, data, mac, self.hash_function)
        
    def reset_environment(self):
        environment = pride.environment
        for field in pride.environment.fields:
            setattr(environment, field, [])
        environment.Instructions = []
        environment.last_creator = None
        
def test_User():
    import pride.interpreter
    python = pride.interpreter.Python()
    user = User(verbosity={"password_verified" : 0})
    data = "This is some test data!"
    packed_encrypted_data = user.encrypt(data)
    assert user.decrypt(packed_encrypted_data) == data
    
if __name__ == "__main__":
    test_User()
    