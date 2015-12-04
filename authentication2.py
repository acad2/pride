import sqlite3
import random
import hashlib
hashes = hashlib

import pride.authentication
import pride.keynegotiation
from pride.authentication import remote_procedure_call, with_arguments

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import openssl
BACKEND = openssl.backend

# generate a secret key
# generate a shared message key server side, encrypt it with the above key
# send the encrypted shared message key to the client
# generate a secret key on the client side and encrypt the shared message key again
# send the twice encrypted key back to the server
# server decrypts the key and sends the singley encrypted key back to the client
# client decrypts the key and has the shared message key

def hash_function(algorithm_name):
    return hashes.Hash(getattr(hashes, algorithm_name)(), backend=BACKEND)
    
def encrypt(data='', key='', iv_size=12, unencrypted_authenticated_data=''):
    assert data and key
    iv = random._urandom(iv_size)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), 
                       backend=BACKEND).encryptor()
    encryptor.authenticate_additional_data(iv + unencrypted_authenticated_data)
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return (ciphertext, encryptor.tag, iv + unencrypted_authenticated_data)
    
def decrypt(ciphertext, key, iv, tag, unencrypted_authenticated_data=''):
    decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), 
                       backend=BACKEND).decryptor()
    decryptor.authenticate_additional_data(iv + unencrypted_authenticated_data)
    return decryptor.update(ciphertext) + decryptor.finalize()
            
def _split_byte(byte):
    """ Splits a byte into high and low order bytes. 
        Returns two integers between 0-15 """
    bits = format(byte, 'b').zfill(8)
    a, b = int(bits[:4], 2), int(bits[4:], 2)
    return a, b
    
def _x_bytes_at_a_time(string, x=16):
    """ Yields x bytes at a time from string """
    while string:
        yield string[:x]
        string = string[x:]
    
class Authentication_Table(object):
    """ Provides an additional factor of authentication. During account
        registration, the server generates an Authentication_Table for the
        newly registered client. The server records this table and sends a 
        copy to the client. When the client attempts to login, the server
        generates a random selection of indices and sends these to the client.
        The client is supposed to return the appropriate symbols from the
        table and the server matches what it expected against the response.
        
        Acts as "something you have", albeit in the form of data. """
    def __init__(self, rows=None, hash_function="sha256"):
        self.hash_function = hash_function
        size = 16
        if not rows:
            characters = [chr(x) for x in xrange(256)]
            rows = []
            for row_number in xrange(size):
                row = []
                while len(row) < size:
                    random_number = random._urandom(1)
                    try:
                        characters.remove(random_number)
                    except ValueError:
                        continue
                    else:
                        row.append(random_number)
                rows.append(''.join(row))
        self.rows = rows
    
    @staticmethod
    def generate_challenge(count=6):
        """ Generates count random pairs of indices, which range from 0-15 """
        return tuple(_split_byte(ord(byte)) for byte in random._urandom(count))
        
    def get_passcode(self, *args): 
        """ Returns a passcode generated from the symbols located at the 
            indices specified in the challenge"""
        return getattr(hashlib, 
                       self.hash_function)((''.join(self.rows[row][index] for 
                                            row, index in args))).digest()
    
    @staticmethod
    def compare(calculation, response):
        """ Compares two iterables in constant time """
        success = False
        for index, byte in enumerate(calculation):
            if response[index] != byte:
                break
        else:
            success = True
        return success
        
    def save(self, _file=None):
        """ Saves the table information to a bytestream. If _file is supplied,
            the bytestream is dumped to the file instead of returned.
            
            WARNING: This bytestream is a secret that authenticates a username
            and should be protected as any password or secure information. """
        text = ''.join(self.rows)
        if _file:
            _file.write(text)
            _file.flush()
        else:
            return text
    
    @classmethod
    def load(cls, text):
        """ Load a bytestream as returned by Authenticated_Table.save and 
            return an authenticated table object. """
        return cls(rows=[row for row in _x_bytes_at_a_time(text)])

        
class Authenticated_Service2(pride.base.Base):
   
    defaults = {"hkdf_table_update_info_string" : "Authentication Table Update",
                "hash_function" : "SHA256", "database_name" : '', 
                "database_type" : "pride.database.Cached_Database",
                "validation_failure_string" :\
                   ".validate: Authorization Failure:\n   ip_blacklisted: {}" +
                   "    session_id logged in: {}\n    method_name: '{}'\n    " +
                   "login allowed: {}    registration allowed: {}"}                
    
    verbosity = {"register" : 'v', "login_stage_two" : 'v',
                 "on_login" : 0, "login" : 'v'}
                 
    database_structure = {"Users" : ("authentication_table_hash BLOB PRIMARY_KEY", 
                                     "authentication_table BLOB", "session_key BLOB")}
                              
    database_flags = {"current_table" : "Users"}
    
    remotely_available_procedures = ("register", "login", "login_stage_two")
    
    mutable_defaults = {"_rate" : dict, "ip_whitelist" : list, "ip_blacklist" : list,
                        "session_id" : dict} # session_id maps session id to username
                        
    inherited_attributes = {"database_structure" : dict, "database_flags" : dict,
                            "remotely_inherited_methods" : tuple}
    
    def __init__(self, **kwargs):
        super(Authenticated_Service2, self).__init__(**kwargs)
        self._load_database()    
        self.hkdf = self.create("cryptography.hazmat.primitives.kdf.hkdf.HKDFExpand",
                                algorithm=getattr(hashes, self.hash_function)(),
                                length=256, info=self.hkdf_table_update_info_string,
                                backend=BACKEND)     
        
    def _load_database(self):
        if not self.database_name:
            _instance_name = '_'.join(name for name in self.instance_name.split("->") if name)
            name = self.database_name = "{}.db".format(_instance_name)
        else:
            name = self.database_name
        self.database = self.create(self.database_type, database_name=name,
                                    database_structure=self.database_structure,
                                    **self.database_flags)
        for table, structure in self.database_structure.items():
            self.database.create_table(table, structure)
            
    def register(self):
        self.alert("Registering new user", level=self.verbosity["register"])
        authentication_table = random._urandom(256)
        hasher = hash_function(self.hash_function)
        hasher.update(authentication_table + "\x00" * 32)
        table_hash = hasher.finalize()
        self.database[table_hash] = {"authentication_table_hash" : table_hash,
                                     "authentication_table" : authentication_table,
                                     "session_key" : "\x00" * 32}
        return authentication_table
        
    def login(self, authentication_table_hash):
        self.alert("Issuing authentication challenge", level=self.verbosity["login"])
        return Authentication_Table.generate_challenge()
        
    def login_stage_two(self, authentication_table_hash, hashed_answer,
                        original_challenge):
        user_id = {"authentication_table_hash" : authentication_table_hash}
        self.alert("{} attempting to log in".format(authentication_table_hash),
                   level=self.verbosity["login_stage_two"])
        try:
            (saved_table,
             session_key) = self.database.query("Users", 
                                                retrieve_fields=("authentication_table",
                                                                 "session_key"),
                                                where=user_id).fetchone()
        except sqlite3.Error:
            macd_challenge = random._random(32 + (32 * 32)) # a random mac and random "hashes"
        else:                
            authentication_table = Authentication_Table.load(saved_table)
            correct_answer = authentication_table.get_passcode(*original_challenge)

            if authentication_table.compare(correct_answer, hashed_answer):  
                self.alert("Authentication success", level=0)
                new_key, macd_challenge = pride.keynegotiation.get_challenge(session_key)
                new_table = self.hkdf.derive(saved_table + ':' + new_key)
                table_hasher = hash_function(self.hash_function)
                table_hasher.update(new_table + ':' + new_key)
                new_table_hash = table_hasher.finalize()      
                self.database[authentication_table_hash] = {"authentication_table_hash" : new_table_hash,
                                                            "authentication_table" : new_table,
                                                            "session_key" : new_key}
                self.on_login(new_table_hash)
        return macd_challenge
        
    def on_login(self, user_id):
        pass
        
    def validate(self, session_id, peername, method_name):
        """ Determines whether or not the peer with the supplied
            session id is allowed to call the requested method """
        if (method_name not in self.remotely_available_procedures or
            peername[0] in self.ip_blacklist or 
            (session_id == '0' and method_name != "register")):
             
            self.alert(self.validation_failure_string,
                      (peername[0] in self.ip_blacklist, session_id in self.session_id,
                       method_name, self.allow_login, self.allow_registration),
                       level=self.verbosity["validate_failure"])
            return False            
        if self.rate_limit and method_name in self.rate_limit:
            try:
                self._rate[session_id][method_name].mark()
            except KeyError:
                latency = pride.utilities.Latency("{}_{}".format(session_id, method_name))
                try:
                    self._rate[session_id][method_name] = latency
                except KeyError:
                    self._rate[session_id] = {method_name : latency}            
            current_rate = self._rate[session_id][method_name].last_measurement
            
            if current_rate < self.rate_limit[method_name]:
                self.alert("Rate of {} calls exceeded 1/{}s ({}); Denying request",
                          (method_name, self.rate_limit[method_name], current_rate),                           
                          level=self.verbosity["validate_failure"])
                return False
        assert peername[0] not in self.ip_blacklist
        assert method_name in self.remotely_available_procedures
        assert session_id != 0 or method_name == "register"
        self.current_session = (session_id, peername)
        self.alert("Authorizing: {} for {}", 
                  (peername, method_name), 
                  level=self.verbosity["validate_success"])
        return True        
        #
        #ip = peername[0]
        #if ip in self.ip_whitelist or ip not in self.ip_blacklist:
        #    if session_id in self.session_id or (session_id == '0' and 
        #                                        ((method_name in ("login", "login_stage_two") and 
        #                                         self.allow_login) or
        #                                        (method_name == "register" and
        #                                         self.allow_registration))):
        #        self.current_session = (session_id, peername)
        #        self.alert("Authorizing: {} for {}", 
        #                  (peername, method_name), 
        #                  level=self.verbosity["validate_success"])
        #        return True
                        
    def __getstate__(self):
        state = super(Authenticated_Service2, self).__getstate__()
        del state["database"]
        return state
        
    def on_load(self, attributes):
        super(Authenticated_Service2, self).on_load(attributes)
        self._load_database()
        
        
class Authenticated_Client2(pride.authentication.Authenticated_Client):   
    
    verbosity = {"register" : 'v', "login" : 'v', 
                 "login_stage_two" : 'v', "register_sucess" : 'v'}
                 
    defaults = {"target_service" : "->Python->Authenticated_Service2",
                "hash_function" : "SHA256", "table_file" : "test_ac2.key",
                "hkdf_table_update_info_string" : "Authentication Table Update"}

    def __init__(self, **kwargs):
        super(Authenticated_Client2, self).__init__(**kwargs)
        self.hkdf = self.create("cryptography.hazmat.primitives.kdf.hkdf.HKDFExpand",
                                algorithm=getattr(hashes, self.hash_function)(),
                                length=256, info=self.hkdf_table_update_info_string,
                                backend=BACKEND)
        
    @remote_procedure_call(callback_name="_store_auth_table")
    def register(self): pass
    
    def _store_auth_table(self, new_table):
        with open(self.table_file, 'wb') as _file:
            _file.write(new_table + "\x00" * 32)
        self.alert("Registered successfully", level=self.verbosity["register_sucess"])
        if self.auto_login:
            self.login()
            
    def _get_auth_table_hash(self):
        with open(self.table_file, 'rb') as _file:
            auth_table = _file.read(256)
            shared_key = _file.read(32)
        hasher = hash_function(self.hash_function)
        hasher.update(auth_table + shared_key)
        self.table_hash = table_hash = hasher.finalize()
        return (self, table_hash), {}
        
    @with_arguments(_get_auth_table_hash)
    @remote_procedure_call(callback_name="login_stage_two")
    def login(self): pass
    
    def _answer_challenge(self, challenge):  
        with open(self.table_file, 'rb') as _file:
            auth_table = _file.read(256)
            shared_key = _file.read(32)
        answer = Authentication_Table.load(auth_table).get_passcode(*challenge)
        self.alert("Answering challenge", level=0)
        return (self, self.table_hash, answer, challenge), {}
        
    @with_arguments(_answer_challenge)
    @remote_procedure_call(callback_name="crack_session_secret")
    def login_stage_two(self, authenticated_table_hash, answer, challenge): pass
    
    def crack_session_secret(self, macd_challenge):
        with open(self.table_file, 'r+b') as _file:
            auth_table = _file.read(256)
            shared_key = _file.read(32)
            new_key = pride.keynegotiation.solve_challenge(shared_key, macd_challenge)
            self.shared_key = new_key
            new_table = self.hkdf.derive(auth_table + ':' + new_key)            
            _file.truncate(0)
            _file.write(new_table)
            _file.write(new_key)
        table_hasher = hash_function(self.hash_function)
        table_hasher.update(new_table + ':' + new_key)
        new_table_hash = table_hasher.finalize()              
        self.table_hash = new_table_hash
        self.on_login()
        
    def on_login(self):
        self.alert("Logged in successfully!", level=0)
        
if __name__ == "__main__":
    service = objects["->Python"].create(Authenticated_Service2)
    client = objects["->Python"].create(Authenticated_Client2, auto_login=False)
    client.register()
    Instruction(client.instance_name, "login").execute(priority=2.5)
    