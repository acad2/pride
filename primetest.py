import heapq
from bff import factor, exponent_search

#def prime_generator():
#    primes = [1]
#    next_number = 1
#    while True:     
#        next_number = (next_number * 2) + 1
#        factors = factor(next_number)
#        for prime, power in factors:
#            if prime not in primes:
#                yield prime                
#                primes.append(prime)        
#                next_number = prime      
                
def prime_generator():
    primes = [1]
    next_number = 1    
    while True:     
        next_number = (next_number * 2) + 1
        if next_number in primes:
            continue
        for prime in primes[1:]:            
            quotient, remainder = divmod(next_number, prime)            
            if not remainder and quotient > 1:                         
                while not remainder:                    
                    quotient, remainder = divmod(quotient, prime)
                quotient = prime * quotient + remainder                
                if quotient not in primes:
                    yield quotient                    
                    next_number = quotient
                    primes.append(quotient)
                break
        else:
            assert next_number not in primes
            yield next_number
            primes.append(next_number)
        
def factor2(number):
    factors = []
    if not number % 2:
        number, remainder, factor = exponent_search(number, 2)
        factors.append(factor)
        
    for prime in prime_generator():
        if not number % prime:
            number, remainder, factor = exponent_search(number, prime)
            factors.append(factor)
        if number in (1, 0):
            break
    return factors
    
def test_prime_generator():
    generator = prime_generator()
    primes = set()
    for count, prime in enumerate(generator):
        assert prime not in primes
        print prime
        primes.add(prime)
        
if __name__ == "__main__":
    #test_prime_generator()
    data = "This"# is an awesome test message. Seriously though, good job."
    bits = ''.join(format(ord(character), 'b').zfill(8) for character in data)
    integer = int(bits, 2)
    print factor2(integer)
