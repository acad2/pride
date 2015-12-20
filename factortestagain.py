import collections
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
    #        print "Skipped a factor; remainder: {}; last remainder: {}".format(remainder, last_remainder)
            prime -= prime_scalar / 2
            prime_scalar = 1
    #        print "Skipped a factor, rolling back", prime, prime_scalar
            last_remainder = 0
        else:
            last_remainder = remainder            
    return factors      
    
def factor4(number):
    factors = []
    original_number = number
    prime = 1
    last_remainder = 0
    remainders = []
    while True:
        if number == 1:
            break
        prime += 1
        
    #    print "{} / {} = {}".format(number, prime, divmod(number, prime))
        quotient, remainder = divmod(number, prime)
        remainders.append(remainder)
        
        if quotient == 1:
    #        print "Skipping forward to last prime ", prime + remainder
            prime += remainder
            quotient, remainder = 1, 0
            
        if not remainder:
            number = quotient
            prime_scalar = prime_exponent = 1
            remainders = [0]
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
            print "Found factor: ", prime, prime_exponent        
            factors.append((prime, prime_exponent))
        
        elif remainder >= quotient: # skip forward
            increment, increment_again = divmod(remainder, quotient)
            prime += increment + 1 if increment_again else 0

        if prime >= original_number or not number:
            break      
        
    return factors
    
def factor5(number, prime=1):
    factors = []
    original_number = number
    last_remainder = 0
    remainders = [0]
    quotients = [0]
    while True:
        if number == 1:
            break
        prime += 1       
        
        quotient, remainder = divmod(number, prime)
    #    print "{} / {} = ({}, {}) {}".format(number, prime, quotient, remainder, float(quotient) / (remainder or quotient))
        remainders.append(remainder)
        quotients.append(quotient)
        if quotient == 1:
    #        print "Skipping forward to last prime ", prime + remainder
            prime += remainder
            quotient, remainder = 1, 0
        elif not quotient:
            factors.append((number, 1))
            break
            
        if not remainder:
            remainders = [0]
            quotients = [0]
            # y is divisible by x. how many powers of x are in y
            exponent = 1
            while True:
                exponent *= 2
    #            print "Checking", prime, exponent
                quotient, remainder = divmod(number, prime ** exponent)
                # number can be 0, 1, or > 1
                if remainder:
                 #   assert quotient > remainder
    #                print "Went too far; going back"
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
                    
    #        print "Found factor: ", prime, exponent, number        
            factors.append((prime, exponent))
            number, remainder = divmod(number, prime ** exponent)
        elif remainder >= quotient: # skip forward
            increment, increment_again = divmod(remainder, quotient)
            print "Skipping forward by", increment + 1 if increment_again else 0
            prime += increment + 1 if increment_again else 0            
        elif remainders[-2] > remainders[-1] and (remainders[-2] and remainders[-1]):
            print "Cycle detected"
    #    #        prime *= 2
    #            #, jumping forward 2x to", prime 
    #    #        remainders = [0]            
            if factors and quotients[-2] - quotients[-1] == 1:
                quotients = [0]
                print "Closed to skip distance!"#, factors, remainders
    #            raw_input()  
        print remainders
        print
        if prime >= original_number or not number:
            break      
        
    return factors
    
def calculate(factors):
    calculated = 1
    for prime, exponent in factors:
        calculated *= pow(prime, exponent)
    return calculated
    
def test_factor(factoring_algorithm, number):
    assert calculate(factoring_algorithm(number)) == number
    
def is_prime(number):
    if not number % 2:
        if number == 2:
            return True
        else:
            return False
    for x in xrange(3, int(ceil(sqrt(number)))):
        if not number % x:
            return False
    else:
        return True
        
def factor_product_of_primes(number):
    return factor5(number, int(ceil(sqrt(number))))
        
if __name__ == "__main__":
    N = int(''.join(str(ord(char)) for char in 
        """MIGHAoGBAN01lQw6DEtRySBBm+Sxl2ivcYmNB6UHovD1m4JOzZKXdHSg/V2S8j5q
        8nb42Up17iYluPqTBxJH49JzoRqc3lGN4QtiSgQYI0DK9dkYlUIJcqdlYtcefhHH
        w7hXtOHOTDx6ffAZaIx8j2BlmtQAZHqSBXRp0Uy4xPyfXMHdbP0DAgEC"""))
    #for x in xrange(2, 10000):
   ##     print "Testing: ", x
   #     #print factor5(x)
  #      test_factor(factor5, x)
    prime1_256 = int("C2438A6117389B2AF0F49DD196765171E1B69B5C3901E3C1FB97BE4C0C636477", 16)
    prime2_256 = int("C165FB8156BB11CBFA5A21F1C120067F1D90EB30EA36036C94811BE4F191E66F", 16)
   # print prime1_256
    #prime1_512 = int("E1CC1A0E2998299BD0AB8EA3DE5D10C306876208C3EAF0BF0E027B492A8B902B7076660557017FAD917570E2636E5E87B7CA5312EF7C99A70FA89938EE654209", 16)
    #prime2_512 = int("E57409113719FA85A70C698968E57349B98C67914B668D39C8C341DFBCDFEEB7210A12F41093B3786893CB8910ADEEBB2E97A7196F3605D11E1858BC986A96D9", 16)
    #prime1_1024 = int("D854833D2A5919E9A6D57F171B8E5698E0AFC40FABE9F1128C776B8808577D2D10EBAC9DC6C4E80C57AE706FEB7E7A82855E3F365636F55E34FD1BFBD29903A72FA9A0C1B0E5DFB6B4E90468C01DE3A54EBF51756706F074645B6B79A882608614CE35FF554B5CA7D7A79D0A3107F1C803A679F008105F98982E83F4FF37F061", 16)
    #prime2_1024 = int("C5AB5D43555C23706172459E937C54E7643D062D74F8218C80052216DE85BA9F76BB2717BE97D92C537D49A65ACAC54720F5E2716C6BE4CB50FD3C5E864E2E96CDFA8BD03AA76C7E59BD1045AD11ED5FE98D1CE56FECB0C7998D1B1BA44345074D559534656C3CB93F4B6AD3C5477482F65C3D80E124D95A485976B59D3EC95B", 16)
    #test_factor(factor5, prime1_256 * prime2_256)
#    print factor5(N)
#    print Timed(factor5, 1)(N)
#    print test_factor(factor5, N)
    #print factor5(11 * 2333)
    print factor_product_of_primes(prime1_256 * prime2_256)
    print "Test Success"
    #print Timed(factor5, 1)(210931203)
    #test = "I Love you Amburrrr :) " * 100
    #binary_test = ''.join(format(ord(character), 'b').zfill(8) for character in test)
    #
    #integer_form = int(binary_test, 2)
   ## print len(binary_test), integer_form
    #factors = factor5(integer_form)
 #  # print len(test), len(str(factors))#, str(factors)
    #decompressed = calculate(factors)
    #_binary = format(decompressed, 'b').zfill(len(binary_test))
    #assert _binary == binary_test
    