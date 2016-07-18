import os
from utilities import bytes_to_integer

Q = 4294967291
P = 340282366524797650892052919558537740179
G = 54521249035780310435070665414012456167

random_number = lambda size : bytes_to_integer(bytearray(os.urandom(size)))

SIZE = 4

def generate_k(q):
    size = SIZE # todo: figure out how to generate appropriately sized numbers based on size of Q
    k = random_number(size)
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
    
if __name__ == "__main__":
    test_authenticated_key_exchange()
    