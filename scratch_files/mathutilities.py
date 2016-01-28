import itertools

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
    
def prime_generator():
    primes = [2]
    yield 2
    for test_number in itertools.count(3, 2):
        for prime in primes:
            if not test_number % prime:
                break
        else:
            yield test_number
            primes.append(test_number)
            
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
            if _number == 1 and not remainder:
                return factor
                
def oldfactor(number):
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
            print "Found factor: ", factor
            
        elif remainder >= quotient: # skip forward
            increment, increment_again = divmod(remainder, quotient)    
            prime += increment + 1 if increment_again else 0            
        if prime >= original_number or not number:
            break       
    return factors
    
def factor(number):
    factors = []        
    for prime in prime_generator():
        if not number % prime:
            number, remainder, factor = exponent_search(number, prime)
 #           print "Found factor: ", factor, number
            factors.append(factor)
        if number in (1, 0):
            break
    return factors
    
def _factor(number):
 #   print "Factoring: ", number
    factors = []    
    if not number % 2:
        number, _, factor = exponent_search(number, 2)
        factors.append(factor)
        if number in (1, 0):
            return factors
    prime = 1
    while True:  
        prime += 2
        quotient, remainder = divmod(number, prime)
 #       print "{} / {} = {} + {}".format(number, prime, quotient, remainder)
        if not remainder:
            number, _, factor = exponent_search(number, prime)
            factors.append(factor)
 #           print "Found factor: ", factor, number
            if number in (1, 0):
                break
        elif remainder >= quotient:
            increment, increment_again = divmod(remainder, quotient)              
            prime += (increment + 1 if increment_again else increment) - 2
    return factors
            
def random_number_generator():
    for x in xrange(3, 8):
        print "Primes with seed: ", x
        generator = prime_generator(primes=[1, x, 2], maintain_sort=False)
        for count in range(16):
            print next(generator)
        
def test_prime_generator():
    generator = prime_generator()
    primes = set()
    for count, prime in enumerate(generator):        
        assert prime not in primes, (prime, primes)
        print prime
        primes.add(prime)
      
def test_factor():
    max_terms = 0
    max_exponent = 0
    max_prime = 2
    prime_count = 0
    for x in xrange(2, 256):
        factors = _factor(x)
        terms = len(factors)
        if terms == 1:
            prime_count += 1
        max_terms = max_terms if max_terms > terms else terms
        _max_exponent = max(exponent for prime, exponent in factors)
        max_exponent = max_exponent if max_exponent > _max_exponent else _max_exponent
        _max_prime = max(prime for prime, exponent in factors)
        max_prime = max_prime if max_prime > _max_prime else _max_prime
       # print "Factored: ", x, factors
        calculated = 1
        for prime, exponent in factors:
            calculated *= prime ** exponent
        assert calculated == x, (calculated, x)
    print "Maximum number of terms: ", max_terms
    print "Maximum prime: ", max_prime
    print "Maximum exponent: ", max_exponent
    print "Total number of primes: ", prime_count
    
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
    test_factor()
    #test_recursion()
    #test_logarithm()