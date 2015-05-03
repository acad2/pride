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

import hashlib
import random

_hash_function = hashlib.sha256
def hash_function(*args):
    arguments = ":".join(str(arg) for arg in args)
    return int(_hash_function(arguments.encode("ascii")).hexdigest(), 16)

def random_bits(n=1024):
    return random.SystemRandom().getrandbits(n) % N
    
N = """pasteme"""
N = int(''.join(N.split()).replace(":", ''), 16)
g = 2

k = hash_function(N, g)
# The above must be the same on both client and server
class Authentication_Service(mpre.base.Base):
    
    def __init__(self, **kwargs):
        self.user_file = {}
        super(Authentication_Service, self).__init__(**kwargs)        
        
    def create_account(self, username, password):
        salt = random_bits(64)
        private_key = hash_function(salt, username, password)
        password_verifier = pow(g, private_key, N)
        _file = self.create("mpre.fileio.Encrypted_File", 
                            self.instance_name + "\\" + username + ".pwv")
        self.user_file[username] = _file.instance_name
        _file.write(salt)
        _file.write(str(password_verifier))
        _file.flush()
                
    def login(self, username, ephemeral_value):
        user_file = self.user_file[username]
        user_file.seek(0)
        H = hash_function
        s = salt = user_file.read(64)
        v = verifier = int(user_file.read())
        b = random_bits()
        B = (k * v + power(g, b, N)) % N
        return B
        
    def generate_session_key(self, A, b, B, v):
        H = self.hash_function
        u = random_scrambling_pattern = H(A, B)
        S_s = pow(A * pow(v, u, N), b, N)
        K_s = H(S_s)
        M_c = yield
        M_s = H(A, M_c, K_s)
        
        
class Authenticated_Client(mpre.base.Base):
    
    def login(self):
        H = hash_function
        I = username = self.username
        a = random_bits()
        A = pow(g, a, N)
        response = yield username + ' ' + str(A)
        s = salt = response[:64]
        B = value = int(response[64:])
        u = random_scrambling_parameter = H(A, B)
        x = H(s, username, getpass.getpass())
        S_c = pow(B - k * pow(g, x, N), a + u * x, N)
        K_c = H(S_c)
        M_c = H(H(N) ^ H(g), H(I), s, A, B, K_c)
        M_s = yield M_c
        