""" compressed factor format - stores an integer representation of a number with
    potentially less bits. Encodes prime numbers and exponents based on bit indices.
    
    Each bit of regular binary is potentially an addition to the exponent of 
    the base number 2. For example:
        
        0001 # 2 ** 0
        0010 # 2 ** 1
        0100 # 2 ** 2
        1000 # 2 ** 3
        ...
        
    With the compressed factor format, the base value is incremented to the 
    next prime every time a 0 bit is encountered in the bit string. Thus:
        
        0001 # 7 ** 1
        0010 # 5 ** 1
        0100 # 3 ** 1
        1000 # 2 ** 1
        
    The exponent for each prime is determined by the number of contiguous 1 bits.
    For example:
        
        1000 # 2 ** 1
        1100 # 2 ** 2
        1101 # (2 ** 2) * (5 ** 1)
        
    Because each '1' bit is usually an exponent of a power significantly larger
    then two, this encoding can represent significantly larger numbers with the
    same quantity of bits. """
            
        
def _generate_primes(_lookahead=3000, memory_allocation=100000000):
    """ A basic implementation of the sieve of Eratosthenes for demo purposes. """    
    composites = bytearray(memory_allocation)
    composites[:2] = "\x01\x01"
    lookahead_range = range(1, _lookahead, 2)
    for x in range(1, _lookahead):
        composites[2 * x] = 1
    for x in lookahead_range:
        composites[3 * x] = 1
    recalculate_at = 2 * _lookahead
    yield 2
    yield 3
    number = 3    
    primes = []
    scalar = {}
    counter = 0
    while True:
        number += 2            
        if not composites[number]:
            yield number
            primes.append(number)
            for x in lookahead_range:
                composites[number * x] = 1
                
def pack_factors(factors):
    """ Pack a series of (prime, power) tuples into a bitstring.
        Depending on the composition of the factors, the returned
        bitstring may represent the integer form of the factored number
        with less bits then the integer form requires. """
    output = ''
    prime_generator = _generate_primes(2, 2 ** 16)
    prime = next(prime_generator)
    for factor, power in factors:
        while prime != factor:
            output += '0'
            prime = next(prime_generator)
        output += '1' * power
    return output
    
def unpack_factors(bits):   
    """ Unpack encoded (prime, power) pairs and compose them into an integer """
    prime_generator = _generate_primes(2, 2 ** 16)
    prime = next(prime_generator)
    power = 0
    output = 1    
    last_bit = len(bits) - 1
    for index, bit in enumerate(bits):
        if bit == '1':
            power += 1
            if index == last_bit:
                output *= prime ** power
        else:
            output *= prime ** power
            power = 0
            prime = next(prime_generator)      
    return output
    