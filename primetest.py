def prime_generator(start=2, n=3):    
    max_quotient = 0
    start = int(ceil(sqrt(n)))
    if not start % 2: # if it's even
        start -= 1 # make it odd
    while True:
        is_prime = True
        for x in xrange(start, n):
            quotient, remainder = divmod(n, x)
            if not remainder:
                is_prime = False
                max_quotient = quotient
            if x >= quotient:
                break
        if is_prime:
            yield n
        n += 2 # don't check even numbers
        
def factor(n):
    factors = []
    x = 2
    while True:
    #for x in xrange(2, n):
        quotient, remainder = divmod(n, x)
        if not remainder:
            factors.append((x, quotient))
        if x >= quotient:
            break
        x += 1
    return factors
      
def _prime_generator(n=3):    
    max_quotient = 0
    while True:
        is_prime = True
        for x in xrange(2, n):
            quotient, remainder = divmod(n, x)
            if not remainder:
                is_prime = False
                max_quotient = quotient
        if is_prime:
            yield n
        n += 1
        
if __name__ == "__main__":
    from pride.decorators import Timed
    def test_break():
        primes = prime_generator(n=100000)
        for x in xrange(100):
            next(primes)
            
    def test_normal():
        _primes = _prime_generator(n=100000)
        for x in xrange(100):
            next(_primes)
    N = int(''.join(str(ord(char)) for char in 
        """MIGHAoGBAN01lQw6DEtRySBBm+Sxl2ivcYmNB6UHovD1m4JOzZKXdHSg/V2S8j5q"""))
       # 8nb42Up17iYluPqTBxJH49JzoRqc3lGN4QtiSgQYI0DK9dkYlUIJcqdlYtcefhHH
       # w7hXtOHOTDx6ffAZaIx8j2BlmtQAZHqSBXRp0Uy4xPyfXMHdbP0DAgEC"""))
    print "Factored N in: ", Timed(factor, 1)(N)
    #for x in xrange(10000, 10021):
    #    print "Factors of {}:".format(x), factor(x)
    #print Timed(test_normal, 1)()
    #print Timed(test_break, 1)()
    #known = [next(_primes) for x in xrange(100)]
    #calculated = [next(primes) for x in xrange(100)]
    #assert known == calculated, len(list(set(known).difference(calculated)))
    #for x in xrange(10):
    #    print next(primes)