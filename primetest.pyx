import heapq
from bff import exponent_search
         
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
    return number, prime, exponent
    
def prime_generator(long long window_size=2 ** 16, primes=None, maintain_sort=True):
    cdef long long window_counter, next_number, skip_count, quotient, remainder, prime, index
    primes = primes or [1, 2]
    seed = iter(primes)
    window_counter = 1
    next_number = 1    
    yield 2
    while True:     
        next_number = (next_number * 2) + 1
   #     print "Testing: ", next_number
        if next_number > window_size * window_counter:
            next_number = next(seed)
            window_counter += 1
            print "Resetting seed... ", next_number
            continue
        if next_number in primes:
            continue
        skip_count = 0
        for index, prime in enumerate(primes[1:]):  
        
            if skip_count:
                skip_count -= 1
                continue

            quotient, remainder = divmod(next_number, prime)
            if not remainder and quotient > 1:                         
                while not remainder:                    
                    quotient, remainder = divmod(quotient, prime)
                quotient = prime * quotient + remainder                
                if quotient not in primes:
                    yield quotient                    
                    next_number = quotient
                    primes.append(quotient)
                    if maintain_sort:
                        primes.sort()
                break
                
            elif remainder >= quotient and quotient: # skip forward
                increment, increment_again = divmod(remainder, quotient)                    
                next_prime = prime + (increment + 1 if increment_again else 0)
                skip_count = 0 
                index += 1
                _prime = prime 
                while _prime < next_prime:
                    skip_count += 1                
                    try:
                        _prime = primes[index + skip_count]
                    except IndexError:
                        skip_count -= 1
                        _prime = primes[index + skip_count]
                        break
        else:            
            yield next_number
            primes.append(next_number)
            if maintain_sort:
                primes.sort()
        
def factor(number):
    cdef long long prime, factor, power
    factors = []        
    for prime in prime_generator():
        if prime > number:
            print "Drew prime greater then N"
            continue
        if not number % prime:
            number, factor, power = exponent_search(number, prime)
            print "Found factor: ", factor, number
            factors.append(factor)
        if number in (1, 0):
            break
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
        assert prime not in primes
   #     print prime
        primes.add(prime)
      
def test_factor():
    for x in xrange(2, 1024):
        factors = factor(x)
  #      print "Factored: ", x, factors
        calculated = 1
        for prime, exponent in factors:
            calculated *= prime ** exponent
        assert calculated == x, (calculated, x)
         
def test_factoring():    
    cdef long long prime, power
    data = "This is an "#awesome test message. Seriously though, good job."
    bits = ''.join(format(ord(character), 'b').zfill(8) for character in data)
    integer = int(bits, 2)
    factors = factor(integer)
    calculated = 1
    for prime, power in factors:
        calculated *= prime ** power
    assert calculated == integer, (calculated, integer)
    print integer
    
if __name__ == "__main__":
   # test_factor()
   # test_prime_generator()
    #random_number_generator()
    test_factoring()