import os
from utilities import bytes_to_integer, integer_to_bytes

Q = 4294967291
P = 340282366524797650892052919558537740179
G = 54521249035780310435070665414012456167

random_number = lambda size : bytes_to_integer(bytearray(os.urandom(size)))

def random_number(q):
    in_bytes = integer_to_bytes(q)
    k = bytearray(os.urandom(len(in_bytes)))
    k_int = bytes_to_integer(k)
    while k_int > q:
        k.pop(-1)
        k_int = bytes_to_integer(k)
    return k_int
   
def generate_k(q):    
    k = random_number(q)
    assert 1 < k < q
    return k
    
def generate_private(Q):
    return generate_k(Q)
    
def generate_public(g, private, p):
    return pow(g, private, p)
    
def generate_r(public_b, private_a, k_a, p):
    return pow(public_b, private_a * k_a, p)
    
def generate_shared_secret(r_b, k_a, p):
    return pow(r_b, k_a, p)
    
def initiate_key_exchange(q=Q, g=G, p=P):
    k = generate_k(q)
    private = generate_private(q)
    public = generate_public(g, private, p)
    return (private, k, public)
    
def advance_key_exchange(public_key_b, private_a, k_a, p=P):
    return generate_r(public_key_b, private_a, k_a, p)
        
def finish_key_exchange(r_b, k_a, p=P):
    return generate_shared_secret(r_b, k_a, p)
        
def test_authenticated_key_exchange():
    k_a = generate_k(Q)
    private_a = generate_private(Q)
    public_a = generate_public(G, private_a, P)
    
    k_b = generate_k(Q)
    private_b = generate_private(Q)
    public_b = generate_public(G, private_b, P)
    
    r_a = generate_r(public_b, private_a, k_a, P)
    r_b = generate_r(public_a, private_b, k_b, P)
    
    secret1 = generate_shared_secret(r_b, k_a, P)
    secret2 = generate_shared_secret(r_a, k_b, P)
    assert secret1 == secret2
    
def test_initiate_advance_finish():
    private_a, k_a, public_a = initiate_key_exchange()
    private_b, k_b, public_b = initiate_key_exchange()
    
    r_a = advance_key_exchange(public_b, private_a, k_a)
    r_b = advance_key_exchange(public_a, private_b, k_b)
    
    secret1 = finish_key_exchange(r_b, k_a)
    secret2 = finish_key_exchange(r_a, k_b)
    assert secret1 == secret2
    
if __name__ == "__main__":
    test_authenticated_key_exchange()
    test_initiate_advance_finish()
    