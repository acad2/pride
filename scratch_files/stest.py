import itertools
from math import ceil, sqrt
import random
import hashlib

#client_numbers = sorted(list(set([ord(character) for character in random._urandom(128)])))
#server_numbers = sorted(list(set([ord(character) for character in random._urandom(128)])))
#shared_numbers = []
#_client_numbers = client_numbers[:]
#print client_numbers
#print server_numbers
#
#while _client_numbers:
#    try:
#        index = server_numbers.index(_client_numbers.pop(0))
#    except ValueError:
#        continue
#    else:
#        shared_numbers.append(server_numbers.pop(index))        
#
#print len(shared_numbers), shared_numbers
#print len(list(set(server_numbers).difference(shared_numbers)))
def is_prime(number):
    if not number % 2 or number == 1:
        return False
    for x in xrange(3, int(ceil(sqrt(number)))):
        if not number % x:
            return False
    else:
        return True
        
client_numbers = [ord(character) for character in random._urandom(256)]
server_numbers = [ord(character) for character in random._urandom(256)]

client_primes = sorted(list(set([number for number in client_numbers if is_prime(number)])))
server_primes = sorted(list(set([number for number in server_numbers if is_prime(number)])))
print "\nClient primes: ", len(client_primes), client_primes
print "\nServer primes: ", len(server_primes), server_primes
shared_primes = sorted(list(set(client_primes).intersection(server_primes)))
print "\nShared primes: ", len(shared_primes), shared_primes

def permutation(primes, count=16):
    _permutation = []
    for index, prime in enumerate(primes):
        _permutation.append(prime)
        for x in xrange(1, 1 + count):
            try:
                _permutation.append(primes[index + x])
            except IndexError:
                break
        if len(_permutation) < count:
            break
        yield _permutation
        _permutation = []
                
for _permutation in itertools.combinations(client_primes, 8):
    #print "Checking: ", _permutation
    if set(_permutation) == set(shared_primes[:8]):
        print "Found matching permutation!: ", _permutation
        break
else:
    print "Failed to find matching permutation"
        