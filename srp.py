"""
  A python implementation of the secure remote password protocol for the
  runtime environment. Authenticated_Service and Authenticated_Client 
  default to using SRP for authentication, and in most cases should
  be used instead of the Secure_Remote_Password component directly.
  
  N, g, and the hash function are customizable. Simply specify them
  as defaults or manually to the constructor. Note that for the protocol
  to operate successfully, both client and server must use the same values
  for N, g, and the hash function.
  
  The following table has been adopted with an adjustment to fit 
  pythons syntax. ^ is originally used to indicate modular exponentiation
  but is implemented in python via the pow function, while in python
  ^ means XOR.
  
  - N:    A large safe prime (N = 2q+1, where q is prime). All arithmetic is done modulo N.
  - g:    A generator modulo N
  - k:    Multiplier parameter (k = H(N, g) in SRP-6a, k = 3 for legacy SRP-6)
  - s:    User's salt
  - I:    Username
  - p:   Cleartext Password
  - H:  One-way hash function
  - ^:    XOR
  - pow: (Modular) Exponentiation
  - u:    Random scrambling parameter
  - a,b:  Secret ephemeral values
  - A,B:  Public ephemeral values
  - x:   Private key (derived from p and s)
  - v:    Password verifier"""

import hashlib
import random
import getpass
import os
import sqlite3

import mpre
import mpre.base
import mpre.errors

class InsecureValueError(Warning): pass

def _hash_function(*args, **kwargs):
    """ Joins each argument with ':' into one concatenated string. Applies
        kwargs["hash_function"] or hashlib.256 if not specified to the arguments.
        return the integer value of the resulting hash_object.hexdigest."""        
    return int(kwargs.get("hash_function", hashlib.sha256)(':'.join(str(arg) for arg in args)).hexdigest(), 16)

def random_bits(n=1024):
    return random.SystemRandom().getrandbits(n) % N
    
def new_salt(size):
    return os.urandom(64)
 
# N, g, and H (the hash function) are configurable, to change them simply supply
# new values to the Secure_Remote_Password components when initializing them. 
# Note these values must be the same for both client and server.
N = int(''.join(str(ord(char)) for char in 
        """MIGHAoGBAN01lQw6DEtRySBBm+Sxl2ivcYmNB6UHovD1m4JOzZKXdHSg/V2S8j5q
        8nb42Up17iYluPqTBxJH49JzoRqc3lGN4QtiSgQYI0DK9dkYlUIJcqdlYtcefhHH
        w7hXtOHOTDx6ffAZaIx8j2BlmtQAZHqSBXRp0Uy4xPyfXMHdbP0DAgEC"""))
g = 2
k = _hash_function(N, g)

ADD_USER = "INSERT INTO Credentials VALUES(?, ?, ?)"
REMOVE_USER = "DELETE FROM Credentials WHERE username = ?"
SELECT_USER = "SELECT salt, verifier FROM Credentials WHERE username = ?"

class Secure_Remote_Password(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({'N' : N,
                     'g' : g,
                     "new_salt" : new_salt,
                     "hash_function" : _hash_function,
                     "verifier_file_system" : "virtual",
                     "database_filename" : "user_registry"})     
        
    def __init__(self, **kwargs):
        self.login_threads = {}
        super(Secure_Remote_Password, self).__init__(**kwargs)        
        
        database = self.database = sqlite3.connect(self.database_filename)
        cursor = database.cursor()        
        cursor.execute("CREATE TABLE IF NOT EXISTS Credentials(" + 
                       "username TEXT PRIMARY KEY, salt TEXT, verifier BLOB)")      
        database.commit()
    
    def register(self, username, password):
        database = sqlite3.connect(self.database_filename)
        database.text_factory = str
        cursor = database.cursor()
        cursor.execute(SELECT_USER, (username, ))
        registered = cursor.fetchone()
        
        if not registered:       
            salt, password_verifier = self.new_verifier(username, password)            
            try:
                cursor.execute(ADD_USER, (username, salt, str(password_verifier)))
            except sqlite3.IntegrityError:
                self.alert("Attempted to register an already existing user '{}'", 
                           [username], level='v')
                database.rollback()
            else:
                database.commit()
            database.close()                
            return True

    def new_verifier(self, username, password):
        salt = self.new_salt(64)
        private_key = self.hash_function(salt, self.hash_function(username + ":" + password))
        password_verifier = pow(self.g, private_key, self.N)        
        return salt, password_verifier
        
    def login(self, username, response):
        self.alert("{} attempting to log in", [username], level='v')
        if username not in self.login_threads:
            A = response
            thread = self.login_threads[username] = self._login(username, A)
            result = next(thread)
        else:
            thread = self.login_threads[username]
            try:
                result = thread.send(response)
            except (StopIteration, InsecureValueError):
                import traceback
                self.alert("Unhandled exception during {} login:\n{}", [username, traceback.format_exc()], level=0)
                del self.login_threads[username]
                result = ''
        return result
        
    def _login(self, username, A):
        N = self.N
        if A % N == 0:
            self.alert("Received an insecure A value from client {}", [username], level='v')
            raise InsecureValueError
        
        database = sqlite3.connect(self.database_filename)
        database.text_factory = str
        cursor = database.cursor()
        
        cursor.execute(SELECT_USER, (username, ))
        registered = cursor.fetchone()
        if not registered:
            # pretend to go through login process with a fake verifier
            salt, verifier = s, v = self.new_verifier(username, self.new_salt(64))
            self.alert("Verifying unregistered user", level=0)
        else:
            salt, verifier = s, v = registered
        v = int(v)    
        H = self.hash_function        
        g = self.g            
        b = random_bits()
        
        B = (k * v + pow(g, b, N)) % N
        M = yield salt + str(B)
        
        u = random_scrambling_parameter = H(A, B)
        K = H( pow(A * pow(v, u, N), b, N))      
        
        if M != H( H(N) ^ H(g), H(username), salt, A, B, K):
            self.alert("Proof of K mismatch from user '{}'", [username], level='v')
            yield None, "Invalid username or password"
        else:
            yield K, H(A, M, K)
          
    def __getstate__(self):
        attributes = super(Secure_Remote_Password, self).__getstate__()
        del attributes["login_threads"]
        del attributes["database"]
        return attributes
        
    def on_load(self, attributes):
        super(Secure_Remote_Password, self).on_load(attributes)
        self.login_threads = {}
        database = self.database = sqlite3.connect(self.database_filename)
        cursor = database.cursor()        
        cursor.execute("CREATE TABLE IF NOT EXISTS Credentials(" + 
                       "username TEXT PRIMARY KEY, salt TEXT, verifier BLOB)")      
        database.commit()
        
        
class SRP_Client(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"username" : "",
                     "password" : '',
                     "thread" : None,
                     "hash_function" : _hash_function,
                     'N' : N,
                     'g' : g})
    
    def __init__(self, **kwargs):
        super(SRP_Client, self).__init__(**kwargs)
        if not self.username:
            raise mpre.errors.ArgumentError("Username attribute not supplied")
        self.a = a = random_bits()
        self.A = pow(self.g, a, self.N)

    def login(self, response=None):
        if not self.thread: 
            self.thread = self._login()
            result = next(self.thread)
        else:
            result = self.thread.send(response)
        return result
        
    def _login(self):
        response = yield self.initial_message()
        _M = yield self.handle_challenge(response)
        yield self.verify_proof(_M)
        
    def initial_message(self):
        return self.username, self.A

    def handle_challenge(self, response):
        H = self.hash_function
        N = self.N
        g = self.g
        salt = response[:64]
        B = int(response[64:])        
        if B % N == 0:
            raise InsecureValueError
            
        u = H(self.A, B)
        if u == 0:
            raise InsecureValueError
            
        x = H(salt, H(self.username + ":" + self.password or getpass.getpass("Please provide the password: ")))         
        K = H( pow(B - k * pow(g, x, N), self.a + u * x, N))
        
        M =  H( H(N) ^ H(g), H(self.username), salt, self.A, B, K)
        return K, M
 
    def verify_proof(self, response):
        client_proof, server_proof, K = response
        if server_proof != self.hash_function(self.A, client_proof, K):
            self.alert("Log in failed; Invalid proof of shared secret received server.", level='v')
        else:
            return True         
         
def test_srp():
    authentication_service = components["Secure_Remote_Password"]
    client = SRP_Client(username="root", verbosity='vvv')
    
    #authentication_service.register("root", "password"):

    print "Attempting to log in"
    salt_B = authentication_service.login(*client.login())
    if not salt_B:
        print "Did not receive salt and B value from server"
    else:
        K, client_proof = client.login(salt_B)
        K, server_proof = authentication_service.login(client.username, client_proof)
        client.login((client_proof, server_proof, K))
        return K
  
if __name__ == "__main__":
    if "Secure_Remote_Password" not in mpre.components:
        mpre.components["Metapython"].create(Secure_Remote_Password)
    if test_srp():
        print "SRP Success"    