""" binary factor format - stores an integer representation of a number with
    potentially less bits. Encodes prime numbers and exponents based on bit indices.
    
    Each bit of regular binary is potentially an addition to the exponent of 
    the base number 2. For example:
        
        0001 # 2 ** 0
        0010 # 2 ** 1
        0100 # 2 ** 2
        1000 # 2 ** 3
        ...
        
    With the binary factor format, the base value is incremented to the 
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
from math import sqrt, ceil            
        
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
            
def prime_generator():
    primes = [1]
    next_number = 1
    while True:     
        next_number = (next_number * 2) + 1
        factors = factor(next_number)
        for prime, power in factors:
            if prime not in primes:
                yield prime                
                primes.append(prime)        
                next_number = prime      
       
def prime_generator():
    primes = [1]
    next_number = 1    
    while True:     
        next_number = (next_number * 2) + 1
        # factors = factor(next_number)
        for prime in primes:
            quotient, remainder = divmod(next_number, prime)
            if not remainder:
                while not remainder:
                    quotient, remainder = divmod(quotient, prime)
                if quotient not in primes:
                    yield quotient
                    primes.append(quotient)
                break
        else:
            assert next_number not in primes
            yield next_Number
            primes.append(next_number)
        #for prime, power in factors:
        #    if prime not in primes:
        #        yield prime                
        #        primes.append(prime)        
        #        next_number = prime 
                
def exponent_search(number, prime):     
    """ A faster then linear search to find x given P and N: P ** x = N """
    exponent = 1
    while True:
        exponent *= 2
    #     print "Checking", prime, exponent
        quotient, remainder = divmod(number, prime ** exponent)
        # number can be 0, 1, or > 1
        if remainder:                     
            # went too far; go back
            exponent /= 2
            scalar = 1
            while True:
                exponent += scalar
                quotient, remainder = divmod(number, prime ** exponent)
                if remainder:
                    exponent -= scalar
                    
                    while True:
                        exponent += 1
                        quotient, remainder = divmod(number, prime ** exponent)
                        if remainder:
                            exponent -= 1
                            break                            
                    break                    
                scalar *= 2
            break    
    number, remainder = divmod(number, prime ** exponent)            
    return number, remainder, (prime, exponent)
    
def logarithm(number):
    if number in (0, 1):
        return None
        
    if not number % 2:
        _number, remainder, factor = exponent_search(number, 2)
        if _number == 1 and not remainder:
            return factor
            
    for divisor in range(3, int(ceil(sqrt(number))) + 1, 2):
        if not number % divisor:
            _number, remainder, factor = exponent_search(number, divisor)
            if _number ==1 and not remainder:
                return factor
    
def factor(number):
    if number in (0, 1):
        return [(number, 1)]
        
    factors = []
    original_number = number
    last_remainder = 0
    remainders = [0]
    quotients = [0]
    
    if not number % 2:
        number, remainder, factor = exponent_search(number, 2)        
        factors.append(factor)
    
    prime = 1    
    while True:
        if number == 1:
            break
        prime += 2    
        
        quotient, remainder = divmod(number, prime)    
        
        if quotient == 1:    
            prime += remainder
            quotient, remainder = 1, 0
        elif not quotient:
            factors.append((number, 1))
            break
            
        if not remainder:
            # y is divisible by x. finds how many powers of x are in y
            number, remainder, factor = exponent_search(number, prime)
            factors.append(factor)
  #          print "Found factor: ", factor
            
        elif remainder >= quotient: # skip forward
            increment, increment_again = divmod(remainder, quotient)    
            prime += increment + 1 if increment_again else 0            
        if prime >= original_number or not number:
            break       
    return factors
    
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
    
def test_pack_factors():
    factors = ((11, 11), (101, 8))
    packed_factors = pack_factors(factors)
    
    #number = 1
    #for factor, power in factors:
    #    number *= factor ** power    
    #packed_integer = format(number, 'b')
    #print len(packed_factors), packed_factors
    #print len(packed_integer), packed_integer   
    
def test_unpack_factors():
    outputs = [unpack_factors(format(x, 'b').zfill(16)) for x in xrange(512)]
    assert len(set(outputs)) == 512, len(set(outputs)) 
    
def test_factor():   
    _max = 0
    for x in xrange(1025):
        factors = factor(x)        
        _max = max(_max, max(power for prime, power in factors))        
        number = 1        
        for prime, power in factors:
            number *= prime ** power
        assert number == x
    print "Highest power found: ", _max
    
def test_recursion():
    factors = [(11, 11), (101, 28)]
    packed1 = pack_factors(factors)
    print len(packed1), packed1, int(packed1, 2)
    integer_form = 1
    for prime, power in factors:
        integer_form *= prime ** power
    
    assert factor(integer_form) == factors      
    factors2 = factor(int(packed1, 2))
    packed2 = pack_factors(factors2)
    print len(packed2), int(packed2, 2)
    
def test_logarithm():
    import itertools
    for x in itertools.count(2):
        print x, logarithm(x)
    
if __name__ == "__main__":
    #test_pack_factors()
    #test_unpack_factors()
    #test_factor()
    #test_recursion()
    test_logarithm()