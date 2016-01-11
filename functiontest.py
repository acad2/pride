import itertools

def even_function(N):
    return 2 * N
    
def odd_function(N):
    _N = 2 * N
    return (_N + 1, _N - 1)
        
def mod_function(x, y, N):
    return (x ** y) % N
 
def discrete_logarithm(g, a, N): 
    # (g ** x) % N == a % N
    right_hand_size = a % N
    cycle = []
    for exponent in itertools.count(1):
        remainder = pow(g, exponent, N)
        cycle.append(remainder)
        
for x in xrange(0, 32):
    print mod_function(16, x, 22)