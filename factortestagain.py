import itertools
from math import ceil, sqrt

from decorators import Timed

def factor(number):
    # n = factor(x) * factor(y)
    factors = []
    original_number = number
    numbers = itertools.count()
    next(numbers) # skip 0
    next(numbers) # skip 1
    for prime in numbers:
  #      print "Next prime: ", prime
  #      print "number is currently: ", number
        _number, remainder = divmod(number, prime)
 #       print "{} / {} = {} + {}".format(number * prime, prime, number, remainder)
        if not remainder:
            number = _number
  #          print "Found a prime factor; {} is divisble by {}".format(number, prime)
            #factors.update((prime, quotient))
            prime_exponent = 1
  #          print "attempting to begin incrementing exponent of {}".format(prime), divmod(number, prime)
            while not number % prime:
                prime_exponent += 1
  #              print "Increment exponent of {} to {}".format(prime, prime_exponent)
                number, remainder = divmod(number, prime)
            factors.append((prime, prime_exponent))
  #          print "Added prime with power: ", prime, prime_exponent
   #         print "Continuing with number: ", number
            #number = _number
            
        if prime >= original_number or not number:
  #          print "breaking: ", prime, number
            break
        
    return factors
    
#print factor(133712938)    
#format(133712938, 'b')                
# 100
# 50 2
# 25 2 2
# 5 5 2 2                


def factor2(number):
    factors = []
    original_number = number
    numbers = itertools.count(3, 2) # start at 3, odd numbers only
    next(numbers) # skip 0    
    for prime in itertools.chain((2, ), numbers):         
        _number, remainder = divmod(number, prime)
        if not remainder:
            number = _number
            prime_exponent = 1
            
            # do an exponential search for the exponent for this prime
            exponent_scaler = 2
            while not number % prime:
                #          print "Testing exponent: ", prime, prime_exponent
                number, remainder = divmod(number, (prime ** prime_exponent))
                prime_exponent *= exponent_scaler
                if not number:
                    break
                if remainder:
                    number = (number * (prime ** prime_exponent)) + remainder
         #           print "Went too far, reset number: ", number
                    # do a linear search now 
                    while not number % prime:
                        prime_exponent += 1
                        number, remainder = divmod(number, prime)
                    break
                exponent_scaler *= 2    
            factors.append((prime, prime_exponent))
        if prime >= original_number or not number:
            break        
    return factors
    
    
#print Timed(factor2, 1)(2 ** 4096)
#print Timed(factor2, 1)(182364123876)
      
def factor3(number):
    factors = []
    original_number = number
    prime = prime_scalar = 1
    last_remainder = 0
    while True:
        prime += prime_scalar
    #    print "{} / {} = {}".format(number, prime, divmod(number, prime))
        _number, remainder = divmod(number, prime)
        prime_scalar *= 2
        if _number == 1:
            prime += remainder
            _number, remainder = 1, 0
            
        if not remainder:
            number = _number
            prime_scalar = prime_exponent = 1
            
            # do an exponential search for the exponent for this prime
            exponent_scaler = 2
            while not number % prime:
                
   #             print "Testing exponent: ", prime, prime_exponent
                number, remainder = divmod(number, (prime ** prime_exponent))
                prime_exponent *= exponent_scaler
                if not number:
                    break
                if remainder:
                    number = (number * (prime ** prime_exponent)) + remainder
         #           print "Went too far, reset number: ", number
                    # do a linear search now 
                    while not number % prime:
                        prime_exponent += 1
                        number, remainder = divmod(number, prime)
                    break
                    
            factors.append((prime, prime_exponent))

        if prime >= original_number or not number:
            break      
        if remainder > last_remainder and (last_remainder and remainder): # skipped a factor
     #       print "Skipped a factor; remainder: {}; last remainder: {}".format(remainder, last_remainder)
            prime -= prime_scalar / 2
            prime_scalar = 1
    #        print "Skipped a factor, rolling back", prime, prime_scalar
            last_remainder = 0
        else:
            last_remainder = remainder            
    return factors      
    
def calculate(factors):
    calculated = 1
    for prime, exponent in factors:
        calculated *= pow(prime, exponent)
    return calculated
    
def test_factor(factoring_algorithm, number):
    assert calculate(factoring_algorithm(number)) == number
    
if __name__ == "__main__":
    N = int(''.join(str(ord(char)) for char in 
        """MIGHAoGBAN01lQw6DEtRySBBm+Sxl2ivcYmNB6UHovD1m4JOzZKXdHSg/V2S8j5q
        8nb42Up17iYluPqTBxJH49JzoRqc3lGN4QtiSgQYI0DK9dkYlUIJcqdlYtcefhHH
        w7hXtOHOTDx6ffAZaIx8j2BlmtQAZHqSBXRp0Uy4xPyfXMHdbP0DAgEC"""))
    #print factor3(N)#Timed(factor3, 1)(N)
    #answer = factor3(2 ** 4096 - 1024)#Timed(factor3, 1)((2 ** 4096) - 1024)
    #calculated = 1
    #for prime, exponent in answer:
    #    calculated *= pow(prime, exponent)
    #assert calculated == (2 ** 4096 - 1024), (calculated, "\n\n", (2 ** 4096 - 1024))
  #  print factor2(100)
    test_factor(factor3, 1012308971230)
    print Timed(factor3, 1)(1012308971230)