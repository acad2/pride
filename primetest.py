import heapq
from bff import exponent_search
         
def prime_generator(window_size=2 ** 16):
    primes = [1, 2]
    seed = iter(primes)
    window_counter = 1
    next_number = 1    
    yield 2
    while True:     
        next_number = (next_number * 2) + 1
        if next_number > window_size * window_counter:
            next_number = next(seed)
            window_counter += 1
         #   print "Resetting seed... ", next_number
            continue
        if next_number in primes:
            continue
        skip_count = 0
        for index, prime in enumerate(primes[1:]):  
        
            if skip_count:
                if skip_count >1:
                    print "Skipping: ", skip_count
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
                #    print "Skipping forward by one: ", _prime
                    try:
                        _prime = primes[index + skip_count]
                    except IndexError:
                        skip_count -= 1
                        _prime = primes[index + skip_count]
                        break
                
  #              if _prime != prime:
           #         print "Calculated a jump to: ", _prime, " from ", prime
        else:            
            yield next_number
            primes.append(next_number)
            primes.sort()
        
def factor(number):
    factors = []        
    for prime in prime_generator():
        if not number % prime:
            number, remainder, factor = exponent_search(number, prime)
            print "Found factor: ", factor, number
            factors.append(factor)
        if number in (1, 0):
            break
    return factors
    
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
        
        
if __name__ == "__main__":
   # test_factor()
   # test_prime_generator()
    data = "This is an "#awesome test message. Seriously though, good job."
    bits = ''.join(format(ord(character), 'b').zfill(8) for character in data)
    integer = int(bits, 2)
    factors = factor(integer)
    calculated = 1
    for prime, power in factors:
        calculated *= prime ** power
    assert calculated == integer, (calculated, integer)
    print integer
    