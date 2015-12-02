import random
import hashlib
hashes = hashlib

import pride.authentication
from pride.authentication import remote_procedure_call, with_arguments

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import openssl
backend = openssl.backend

# generate a secret key
# generate a shared message key server side, encrypt it with the above key
# send the encrypted shared message key to the client
# generate a secret key on the client side and encrypt the shared message key again
# send the twice encrypted key back to the server
# server decrypts the key and sends the singley encrypted key back to the client
# client decrypts the key and has the shared message key

def encrypt(data='', key='', unencrypted_authenticated_data='', iv_size=12):
    assert data and key
    iv = random._urandom(iv_size)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), 
                       backend=backend).encryptor()
    encryptor.authenticate_additional_data(iv + unencrypted_authenticated_data)
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return (ciphertext, encryptor.tag, iv + unencrypted_authenticated_data)
    
def decrypt(ciphertext, key, unencrypted_authenticated_data, iv, tag):
    decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), 
                       backend=backend).decryptor()
    if unencrypted_authenticated_data:
        decryptor.authenticate_additional_data(unencrypted_authenticated_data)
    return decryptor.update(ciphertext) + decryptor.finalize()
    
def create_session(key, size=32):
    shared_key = random._urandom(size)
    encrypted_shared_key, key_tag, key_iv = encrypt(shared_key, key=key)
    return encrypted_shared_key, key_tag, key_iv, shared_key
    
# ... encrypted key arrives at client
def join_session(encrypted_shared_key, size=32):
    key = random._urandom(32)
    return encrypt(data=encrypted_shared_key, key=key), key
    
# ... server decrypts and returns
# ... client decrypts and has the key

def unlock_session(encrypted_shared_key, key, tag, iv):
    return decrypt(encrypted_shared_key, key, iv, iv, tag)

class Authenticated_Service2(pride.base.Base):
   
    defaults = {"hkdf_table_update_info_string" : "Authentication Table Update",
                "hash_function" : "SHA256"}
    
    verbosity = {"register" : 0, "create_session" : 0, "login_stage_two" : 0,
                 "on_login" : 0}
                 
    def __init__(self, **kwargs):
        super(Authenticated_Service2, self).__init__(**kwargs)
        self.key = random._urandom(32)
        self.database = self.create("pride.database.Database", database_name="testas2.db")
        self.database.create_table("Users", ("authentication_table_hash BLOB PRIMARY KEY",
                                             "authentication_table BLOB", "shared_key BLOB"))
        self.hkdf = self.create("cryptography.hazmat.primitives.kdf.hkdf.HKDFExpand",
                                algorithm=getattr(hashes, self.hash_function),
                                length=256, info=self.hkdf_table_update_info_string,
                                backend=backend)
    def register(self):
        self.alert("Registering new user", level=self.verbosity["register"])
        encrypted_shared_key, key_tag, key_iv, shared_key = create_session(self.key)
        authentication_table = random._urandom(256)
        hash_function = getattr(hashes, self.hash_function)
        print type(hash_function), hash_function, hashes, self.hash_function
        self.database.insert_into("Users", (hash_function(authentication_table + shared_key).digest(),
                                            authentication_table, shared_key,
                                            tag, iv))
        encrypted_table, table_tag, table_iv = encrypt(authentication_table, shared_key)
        return (encrypted_shared_key, tag, iv, 
                encrypted_table, table_tag, table_iv)
        
    def create_session(self, key_tag, key_iv, twice_encrypted_key):
        self.alert("Unlocking session key", level=self.verbosity["create_session"])
        return unlock_session(twice_encrypted_key, self.key, key_tag, key_iv)
        
    def login(self, authentication_table_hash):
        return Authentication_Table.generate_challenge()
        
    def login_stage_two(self, authentication_table_hash, hashed_answer,
                        original_challenge):
        user_id = {"authentication_table_hash" : authentication_table_hash}
        hash_function = getattr(hashes, self.hash_function)     
        self.alert("{} attempting to log in".format(authentication_table_hash),
                   level=self.verbosity["login_stage_two"])
        try:
            (saved_table, 
            shared_key,
            history) = self.database.query("Users", 
                                            retrieve_fields=("authentication_table", 
                                                            "shared_key", "history"),
                                            where=user_id).fetchone()
        except sqlite3.Error:
            macd_challenge = random._random(32 + (32 * 32)) # a random mac and random "hashes"
        else:                
            authentication_table = Authentication_Table.load(saved_table)
            correct_answer = authentication_table.get_passcode(*original_challenge)
            
            if authentication_table.compare(correct_answer, hashed_answer):            
                new_table = self.hkdf_table.derive(saved_table + ':' + shared_key)
                new_table_hash = hash_function(new_table + ':' + shared_key).digest()
                new_key, macd_challenge = pride.keynegotiation.get_login_challenge(shared_key)           
                self.database.update("Users", where=user_id, 
                                    arguments={"authentication_table_hash" : new_table_hash,
                                                "authentication_table" : new_table,
                                                "shared_key" : new_key})
                self.on_login(new_table_hash)
        return macd_challenge
        
    def on_login(self, user_id):
        pass
        
    def validate(self, *args, **kwargs):
        return True
        
class Authenticated_Client2(pride.authentication.Authenticated_Client):   
    
    verbosity = {"register" : 0, "create_session" : 0, "login" : 0, 
                 "login_stage_two" : 0}
                 
    defaults = {"target_service" : "->Python->Authenticated_Service2",
                "hash_function" : "SHA256"}

    @remote_procedure_call(callback_name="create_session")
    def register(self): pass
    
    def _store_auth_table(self, encrypted_key, key_tag, key_iv,
                                encrypted_auth_table, table_tag, table_iv):
        self.auth_table = encrypted_auth_table
        self.table_info = (table_tag, table_iv)
        key = self.secret_key = random._urandom(32)
        twice_encrypted_key, key2_tag, key2_iv = encrypt(encrypted_key, key)
        self.key_info = key2_tag, key2_iv
        return (self, key_tag, key_iv, twice_encrypted_key), {}
        
    @with_arguments(_store_auth_table)
    @remote_procedure_call(callback_name="decrypt_key")
    def create_session(self): pass

    def decrypt_key(self, encrypted_key):
        shared_key = self.shared_key = decrypt(encrypted_key, self.secret_key)
        self.auth_table = decrypt(self.auth_table, shared_key)
        if self.auto_login:
            self.login()
    
    def _get_auth_table_hash(self):
        table_hash = getattr(hashes, self.hash_function)(self.auth_table + self.shared_key).digest()
        self.table_hash = table_hash
        return (self, table_hash), {}
        
    @with_arguments(_get_auth_table_hash)
    @remote_procedure_call(callback_name="login_stage_two")
    def login(self): pass
    
    def _answer_challenge(self, challenge):
        hash_function = getattr(hashes, self.hash_function)
        table_hash = hash_function(self.auth_table + self.shared_key).digest()
        answer = Authentication_Table.load(self.auth_table).get_passcode(*challenge)
        return (self, table_hash, hash_function(answer).digest()), {}
        
    @with_arguments(_answer_challenge)
    @remote_procedure_call(callback_name="crack_session_secret")
    def login_stage_two(self, authenticated_table_hash, hashed_answer, original_challenge): pass
    
    def crack_session_secret(self, macd_challenge):
        shared_key, _ = pride.keynegotiation.client_attempt_login(macd_challenge)
        self.shared_key = shared_key
        self.on_login()
        
    def on_login(self):
        self.alert("Logged in successfully!", level=0)
        
if __name__ == "__main__":
    service = objects["->Python"].create(Authenticated_Service2)
    client = objects["->Python"].create(Authenticated_Client2, auto_login=False)
    print client.target_service
    client.register()