"""
  N    A large safe prime (N = 2q+1, where q is prime)
       All arithmetic is done modulo N.
  g    A generator modulo N
  k    Multiplier parameter (k = H(N, g) in SRP-6a, k = 3 for legacy SRP-6)
  s    User's salt
  I    Username
  p    Cleartext Password
  H()  One-way hash function
  ^    (Modular) Exponentiation
  u    Random scrambling parameter
  a,b  Secret ephemeral values
  A,B  Public ephemeral values
  x    Private key (derived from p and s)
  v    Password verifier"""

import mpre
import mpre.base

import hashlib
import random
import getpass
import os

_hash_function = hashlib.sha256
def hash_function(*args):
    return int(_hash_function(':'.join(str(arg) for arg in args)).hexdigest(), 16)

def random_bits(n=1024):
    return random.SystemRandom().getrandbits(n) % N
    
N = """MIGHAoGBAN01lQw6DEtRySBBm+Sxl2ivcYmNB6UHovD1m4JOzZKXdHSg/V2S8j5q
8nb42Up17iYluPqTBxJH49JzoRqc3lGN4QtiSgQYI0DK9dkYlUIJcqdlYtcefhHH
w7hXtOHOTDx6ffAZaIx8j2BlmtQAZHqSBXRp0Uy4xPyfXMHdbP0DAgEC"""
N = int(''.join(str(ord(char)) for char in N))
g = 2

k = hash_function(N, g)
# The above must be the same on both client and server
class Secure_Remote_Password(mpre.base.Base):
    
    def __init__(self, **kwargs):
        self.user_file = {}
        self.login_threads = {}
        self.hash_function = hash_function
        super(Secure_Remote_Password, self).__init__(**kwargs)        
        
    def register(self, username, password):
        salt = os.urandom(64)
        hash_function = self.hash_function
        private_key = hash_function(salt, hash_function(username + ":" + password))
        password_verifier = pow(g, private_key, N)
        _file = self.create("mpre.fileio.Encrypted_File", 
                            "virtual" + "\\" + username + ".pwf")
        self.user_file[username] = _file.instance_name
        _file.write(salt)
        _file.write(str(password_verifier))
        _file.flush()
        return True
        
    def login(self, username, response):
        if username not in self.login_threads:
            A = response
            thread = self.login_threads[username] = self._login(username, A)
            result = next(thread)
        else:
            thread = self.login_threads[username]
            try:
                result = thread.send(response)
            except (StopIteration, Exception):
                del self.login_threads[username]
                result = ''
        return result
        
    def _login(self, username, A):
        if A % N == 0:
            raise Exception
        try:
            user_file_reference = self.user_file[username]
        except KeyError:
            self.on_nonexistant_username_login(username)
            
        user_file = mpre.components[user_file_reference]
        user_file.seek(0)
        data = user_file.read()
        H = self.hash_function
        s = salt = data[:64]
       
        v = verifier = int(data[64:])
        b = random_bits()
        
        B = (k * v + pow(g, b, N)) % N
        M = yield salt + str(B)
        
        u = random_scrambling_parameter = H(A, B)
        K = H( pow(A * pow(v, u, N), b, N))      
        
        if M != H( H(N) ^ H(g), H(username), salt, A, B, K):
            raise Exception
        else:
            yield K, H(A, M, K)
        
    def on_nonexistant_username_login(self, username):
        self.alert("Received a login attempt by unregistered user {}", [username], level=0)
        # to do: carry out pretend login procedure with fake verifier
        # as suggested in tools.ietf.org/rfc/rfc5054.txt 2.5.1.3.
        raise Exception
        
    
class SRP_Client(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"username" : "",
                     "thread" : None})
    
    def __init__(self, **kwargs):
        self.hash_function = hash_function
        super(SRP_Client, self).__init__(**kwargs)
        if not self.username:
            raise errors.ArgumentError("Username attribute not supplied")
        self.a = a = random_bits()
        self.A = pow(g, a, N)

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
        print response
        salt = response[:64]
        B = int(response[64:])
        H = self.hash_function
        if B % N == 0:
            raise Exception
            
        u = H(self.A, B)
        if u == 0:
            raise Exception
            
        x = H(salt, H(self.username + ":" + getpass.getpass("Please provide the password: ")))         
        K = H( pow(B - k * pow(g, x, N), self.a + u * x, N))
        
        M =  H( H(N) ^ H(g), H(self.username), salt, self.A, B, K)
        return K, M
 
    def verify_proof(self, response):
        client_proof, server_proof, K = response
        if server_proof != self.hash_function(self.A, client_proof, K):
            raise Exception
        return True        
 
def start_login(username):
    a = random_bits()
    A = pow(g, a, N)
    return (username + " " + str(A), a, A)
    
def handle_challenge(username, a, A, challenge, hash_function=hash_function):
    salt = challenge[:64]
    B = int(challenge[64:])
    H = hash_function
    if B % N == 0:
        raise Exception
        
    u = H(A, B)
    if u == 0:
        raise Exception
        
    x = H(salt, H(username + ":" + getpass.getpass("Please provide the password: ")))         
    K = H( pow(B - k * pow(g, x, N), a + u * x, N))
    
    M =  H( H(N) ^ H(g), H(username), salt, A, B, K)
    return K, M

def verify_proof(client_proof, server_proof, K, A, hash_function=hash_function): 
        if server_proof != hash_function(A, client_proof, K):
            raise Exception
        return True       
        
def test():
    authentication_service = Secure_Remote_Password()
    client = SRP_Client(username="root")
    authentication_service.register("root", "password")
    salt_B = authentication_service.login(*client.login())
    
    K, client_proof = client.login(salt_B)
    K, server_proof = authentication_service.login(client.username, client_proof)
    client.login((client_proof, server_proof, K))
    return K
    
if __name__ == "__main__":
    if test():
        print "Success"