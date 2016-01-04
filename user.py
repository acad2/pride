import sys
import os
import getpass
import random

import pride.base
import pride.security
import pride.shell

class InvalidUsername(BaseException): pass

class User(pride.base.Base):
    """ A User object for managing secure information and client accounts.
        A user is capable of performing manipulation of secure data,
        including encryption and decryption. The user object is responsible
        for deriving and holding keys required for such manipulation. """
    defaults = {# security configuration options    
                # these may need to update with time
                "hash_function" : "SHA256", "kdf_iteration_count" : 100000, 
                "salt_size" : 16, "key_length" : 32, "iv_size" : 16,
                
                # these will probably be updated less frequently
                "encryption_mode" : "GCM", "encryption_algorithm" : "AES",
                
                # login/key derivation can be bypassed by supplying keys directly
                # note that encryption key, salt, and mac key must be supplied to
                # skip the login/key derivation process
                # filesystem_key is used to access nonindexable files in ->User->File_System
                "encryption_key" : bytes(), "salt" : bytes(), "mac_key" : bytes(),
                "file_system_key" : bytes(),
                
                # similarly, username may be assigned instead of prompted. 
                "username" : '', 
                
                # These may be changed for specific application needs
                "hkdf_mac_info_string" : "{} Message Authentication Code Key",
                "hkdf_encryption_info_string" : "{} Encryption Key",
                "hkdf_file_system_info_string" : "{} File_System key",
                "password_prompt" : "{}: Please provide the pass phrase or word: ",
                
                # the salt and verifier file are stored in the ->User->File_System
                # nonindexable files have the filename hashed upon storing/search
                "salt_filetype" : "pride.fileio.Database_File",
                "verifier_filetype" : "pride.fileio.Database_File",
                "salt_indexable" : False, "verifier_indexable" : False,
                
                "launcher_type" : "pride.interpreter.Python"}
    
    parser_ignore = ("mac_key", "encryption_key", "hkdf_mac_info_string", 
                     "hkdf_encryption_info_string", "hkdf_file_system_info_string",
                     "password_prompt", "iv_size", "verifier_filetype",
                     "salt_indexable", "kdf_iteration_count",
                     "encryption_mode", "encryption_algorithm",
                     "launcher_type", "verifier_indexable",
                     "salt_size", "salt_filetype", "salt")
    
    flags = {"_password_verifier_size" : 32, "_reset_encryption_key" : False,
             "_reset_file_system_key" : False}
    
    verbosity = {"password_verified" : 'v', "invalid_password" : 0}
    
    def _get_password(self):
        return getpass.getpass(self.password_prompt.format(self.reference))
    password = property(_get_password)
    
    def _get_username(self):
        if not self._username:
            username_prompt = "{}: Please provide a username: ".format(self.reference)
            self._username = raw_input(username_prompt, must_reply=True)
        return self._username
    def _set_username(self, value):
        self._username = value
    username = property(_get_username, _set_username)   
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.create("pride.fileio.File_System")        
        login_success = self.encryption_key and self.mac_key and self.file_system_key and self.salt
        while not login_success:
            try:
                self.login()
            except (InvalidUsername, pride.security.InvalidTag): # failed to open password verifier file
                self.username = ''
                if self._reset_encryption_key:
                    self.encryption_key = bytes()
                self.alert("Login failed", level=self.verbosity["invalid_password"])
                continue
            else:
                login_success = True      
        self.create("pride.shell.Command_Line")       
                        
    def login(self):
        """ Attempt to login as username using a password. Upon success, the
            users encryption and mac key are derived and stored in memory.
            Upon failure, the prompt is repeated. """
        if self.file_system_key:
            backup = self.file_system_key
            self.file_system_key = b''
        else:
            backup = ''
                
        if not self.salt:
            with self.create(self.salt_filetype, # uses Database_Files by default
                             "{}_salt.bin".format(self.username), 
                             "a+b", indexable=self.salt_indexable) as _file:                 
                _file.seek(0)
                salt = _file.read(self.salt_size)
                if not salt:
                    salt = random._urandom(self.salt_size)
                    _file.write(salt)
        else:
            salt = self.salt            
        key_length = self.key_length
        if key_length < 16:
            raise ValueError("Invalid key length supplied ({})".format(key_length))
        
        kdf = invoke("pride.security.key_derivation_function", 
                          algorithm=self.hash_function, length=key_length, 
                          salt=salt, iterations=self.kdf_iteration_count)
        master_key = kdf.derive(self.username + ':' + self.password)
        
        hkdf_options = {"algorithm" : self.hash_function, "length" : key_length,
                        "info" : self.hkdf_encryption_info_string.format(self.username + salt)}      
        
        if not self.encryption_key:
            encryption_kdf = invoke("pride.security.hkdf_expand", **hkdf_options)
            self.encryption_key = encryption_kdf.derive(master_key)                
            self._reset_encryption_key = True
                        
        # Create a password verifier by creating/finding a nonindexable 
        # encrypted file.
        with self.create(self.verifier_filetype,
                         "{}_password_verifier.bin".format(self.username),
                         "a+b", indexable=False, encrypted=True) as _file:
            _file.seek(0)
            verifier = _file.read()
            if verifier:
                assert verifier == self.username, verifier
            else:
                if pride.shell.get_permission("{}: username '{}' does not exist. Create it?: (y/n) ".format(self, self.username)):
                    _file.write(self.username)
                else:
                    _file.delete_from_filesystem()
                    raise InvalidUsername
        self.salt = salt          
        
        if not backup:
            hkdf_options = {"info" : self.hkdf_file_system_info_string.format(self.username + salt)}
            file_system_kdf = invoke("pride.security.hkdf_expand", **hkdf_options)
            self.file_system_key = file_system_kdf.derive(master_key)            
        else:
            self.file_system_key = backup
            
        if not self.mac_key:
            hkdf_options["info"] = self.hkdf_mac_info_string.format(self.username + salt)        
            mac_kdf = invoke("pride.security.hkdf_expand", **hkdf_options)
            self.mac_key = mac_kdf.derive(master_key)
                                
    def encrypt(self, data, extra_data=''):
        """ Encrypt and authenticates the supplied data; Authenticates, but 
            does not encrypt, any extra_data. The data is encrypted using the 
            Users encryption key. Returns packed encrypted bytes. 
            
            Encryption is done via AES-256-GCM. """
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
        
    def verify(self, macd_data):
        """ Verifies data with the mac returned by authenticate. Data that is 
            verified has two extremely probable guarantees: that it did indeed
            come from who an authorized party, and that it was not manipulated 
            by unauthorized parties in transit. """
        return pride.security.verify_mac(self.mac_key, macd_data, self.hash_function)
                
def test_User():
    import pride.interpreter
    python = pride.interpreter.Python()
    user = User(verbosity={"password_verified" : 0})
    data = "This is some test data!"
    packed_encrypted_data = user.encrypt(data)
    assert user.decrypt(packed_encrypted_data) == data
    
if __name__ == "__main__":
    test_User()
    