import itertools
import random
import operator

def xor(input_one, input_two):
    return map(operator.xor, input_one, input_two)
    



    
print random_numbers_xor
print random_numbers2_xor
together = random_numbers_xor ^ random_numbers2_xor
print together
print together ^ random_numbers_xor
#print xor(random_numbers, random_numbers2)
    
def get_possible_values(xor_sum, potential_numbers, input_count):
    possibilities = []
    test_sum = 0
    for combination in itertools.combinations(potential_numbers, input_count):
        for integer in combination:
            test_sum ^= integer
        if test_sum == xor_sum:
            possibilities.append(combination)
        test_sum = 0
    return possibilities        
        
print get_possible_values(1 ^ 3 ^ 9 ^ 11, (1, 3, 5, 7, 9, 11), 4)  

random_numbers = [ord(character) for character in random._urandom(128)]
random_numbers2 = [ord(character) for character in random._urandom(128)]

random_numbers_xor = 0
for number in random_numbers:
    random_numbers_xor ^= number
    
random_numbers2_xor = 0
for number in random_numbers2:
    random_numbers2_xor ^= number
    
# (1 ^ 2 ^ 3 ^ 5 ^ 7 ^ 9) ^ (7 ^ 8 ^ 9 ^ 11 ^ 13 ^ 15)
"0000 0001"     "0000 0111"
"0000 0010"     "0000 1000"
"0000 0011"     "0000 1001"
"0000 0101"     "0000 1011"
"0000 0111"     "0000 1101"
"0000 1001"     "0000 1111"
"0000 1001"     "0000 0111"
11              15



# (1 ^ 3 ^ 5 ^ 11 ^ 13 ^ 15)


