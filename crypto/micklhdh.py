import os
from utilities import bytes_to_integer

Q = 4294967291
P = 340282366524797650892052919558537740179
G = 54521249035780310435070665414012456167

random_number = lambda size : bytes_to_integer(bytearray(os.urandom(size)))

SIZE = 4

K_a = random_number(SIZE)
Private_a = random_number(SIZE)

K_b = random_number(SIZE)
Private_b = random_number(SIZE)

assert 1 < K_a < Q
assert 1 < K_b < Q

Public_a = pow(G, Private_a, P)
#Public_b = pow(G, Private_b, P)
Public_b = 95446980204587512202682632596933263866

R_a = pow(Public_b, Private_a * K_a, P)
R_b = pow(Public_a, Private_b * K_b, P)

print pow(R_a, K_b, P)
print pow(R_b, K_a, P)