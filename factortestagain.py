import itertools
from math import ceil, sqrt

from pride.decorators import Timed

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
                prime_exponent *= exponent_scaler
      #          print "Testing exponent: ", prime, prime_exponent
                number, remainder = divmod(number, (prime ** prime_exponent))
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
    return factors
    
    
#print Timed(factor, 1)(2 ** 64)
#print Timed(factor2, 1)(182364123876)
      