import itertools
from mathutilities import exponent_search
         
#def prime_generator(window_size=2 ** 8, primes=None):
#    for window in prime_window(window_size, primes):
#        for prime in window:
#            yield prime
  
def prime_generator2():
    primes = [1, 2, 3, 5]
    progress = 3
    while True:
        current_number = 1
        current_primes = []
        for prime in primes[1:progress]:
            current_primes.append(prime)
            current_number *= prime
       
        for prime in (prime for prime in primes if prime not in current_primes):
            next_prime = current_number + prime         
       #     print "Added: ", current_number, prime, next_prime
            yield next_prime
            primes.append(next_prime)
            #current_primes.append(current_number + prime)           
            
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
        
def prime_window(window_size=2 ** 8, primes=None):
    primes = primes or [2, 3]
    seed = iter(primes)
    window_counter = 1
    skip_count = prime_index = 0
    next_number = primes[0]    
   # yield next_number
    while True:     
        next_number = (next_number * 2) + 1        
        print "Next candidate: ", next_number
        if next_number > window_size * window_counter:
            try:
                next_number = next(seed)
            except StopIteration:
                window_counter += 1   
                yield sorted(primes[prime_index:])
                prime_index = len(primes)
                seed = iter(primes)
            continue
            
        if next_number in primes:
            continue            
        
        for prime in primes:          
     #       if skip_count:
     #           skip_count -= 1
     #           continue

            quotient, remainder = divmod(next_number, prime)
            print "Divided: ", next_number, prime, quotient, remainder
            if not remainder:
                if quotient in primes:
                    break
                                    
                print "Found potentially composite factor of: ", next_number, quotient
                while not remainder:                    
                    quotient, remainder = divmod(quotient, prime)
                quotient = prime * quotient + remainder                
                if quotient > 1 and quotient not in primes:
                   # print "Found prime: ", quotient                  
                   # if quotient == 25:
                   #     print "Found incorrect prime: ", quotient, prime, remainder
                   #     raise SystemExit()
                    next_number = quotient
                    #primes.append(quotient)
         #           primes.sort()
                break  
         #   elif remainder >= quotient and quotient: # skip forward
         #       increment, increment_again = divmod(remainder, quotient)                    
         #       next_cycle = prime + (increment + 1 if increment_again else 0)
         #       skip_count = 0 
         #       index = primes.index(prime)
         #       _prime = prime 
       # #        print index, _prime, next_cycle, len(primes)
         #       try:
         #           while primes[index + skip_count] < next_cycle:
         #               skip_count += 1
         #       except IndexError:
         #           pass
                    #try:
                    #    _prime = primes[index + skip_count]
                    #except IndexError:
                    #    skip_count -= 1
                    #    _prime = primes[index + skip_count]
                    #    break                 
        else:               
            if next_number == 25:
                raise SystemExit("Failed")
            print "Found prime: ", next_number
            primes.append(next_number)
        #    primes.sort()
           
            
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
    for prime in prime_generator2():
        if not number % prime:
            number, remainder, factor = exponent_search(number, prime)
            print "Found factor: ", factor
            factors.append(factor)
        if number in (1, 0):
            break
    return factors
   
def _factor(number):
    factors = []    
    if not number % 2:
        number, _, factor = exponent_search(number, 2)
        factors.append(factor)
        
    prime = 1
    while True:
        prime += 2
        quotient, remainder = divmod(number, prime)
        if not remainder:
            number, _, factor = exponent_search(number, prime)
            print "Found factor: ", factor
            factors.append(factor)
        elif remainder >= quotient:
            increment, increment_again = divmod(remainder, quotient)  
            print "Skipping: ", prime, increment
            prime += increment + 1 if increment_again else increment          
        else:
            print number, prime, quotient, remainder
            
def random_number_generator():
    for x in xrange(3, 8):
        print "Primes with seed: ", x
        generator = prime_generator(primes=[1, x, 2], maintain_sort=False)
        for count in range(16):
            print next(generator)
        
def test_prime_generator():    
    primes = set()
    for prime in prime_generator():    
        assert prime not in primes, (prime, primes)            
        primes.add(prime)
        print prime
        
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
    #random_number_generator()
    data = "This is an awe"#some test message. Seriously though, good job."
    bits = ''.join(format(ord(character), 'b').zfill(8) for character in data)
    integer = int(bits, 2)
    factors = factor(integer)
    calculated = 1
    for prime, power in factors:
        calculated *= prime ** power
    assert calculated == integer, (calculated, integer)
    print integer
    