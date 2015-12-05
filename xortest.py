import itertools
import random
import operator

def xor(input_one, input_two):
    return map(operator.xor, input_one, input_two)
    
random_numbers = [ord(character) for character in random._urandom(128)]
random_numbers2 = [ord(character) for character in random._urandom(128)]

random_numbers_xor = 0
for number in random_numbers:
    random_numbers_xor ^= number
    
random_numbers2_xor = 0
for number in random_numbers2:
    random_numbers2_xor ^= number
    
print random_numbers_xor
print random_numbers2_xor
together = random_numbers_xor ^ random_numbers2_xor
print together
print together ^ random_numbers_xor
#print xor(random_numbers, random_numbers2)
    
xor_sum = 1 ^ 3 ^ 9 ^ 11
test_sum = 0
possibilities = []
for combination in itertools.combinations((1, 3, 5, 7, 9, 11), 4):
    for integer in combination:
        test_sum ^= integer
    if test_sum == xor_sum:
        possibilities.append(combination)
print possibilities        
        