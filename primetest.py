import pprint

def test_primality(number):
    factor, remainder = divmod(number, 2)
    if remainder:
        while factor > remainder:
           # print factor, remainder
            factor -= 1
            remainder += 2            
       # print number
       # print factor, remainder
        if factor != remainder:
            return True
    return False
    
def test_primality2(number):
    for x in xrange(2, number):
        if not number % x:
            return False
    return True        
    
if __name__ == "__main__":
    primes1 = [(x, test_primality(x)) for x in xrange(3, 100)]
    primes2 = [(x, test_primality2(x)) for x in xrange(3, 100)]
    print primes1 == primes2
    print
    pprint.pprint(zip(primes1, primes2))