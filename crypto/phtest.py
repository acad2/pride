ODD_NUMBERS = list(set(((number * 2) | 1 for number in range(256))))

def permutation(data, key=ODD_NUMBERS):    
    for index in reversed(xrange(1, len(data))):        
        right_byte = data[index] # right_byte = 16 bit unsigned int
        right_byte += key[index] # increment, potentially overflowing low order byte
        data[index - 1] = (data[index - 1] + (right_byte >> 8)) & 255 # add any bits in high order byte to next byte
        
        right_byte &= 255 # mask to 8 bit unsigned int
        data[index] = right_byte                    
        
        data[index - 1] ^= ((right_byte >> 5) | (right_byte << (8 - 5))) & 255 # rotate right; provides diffusion
        
    data[0] = (data[0] + key[0]) & 255         
    return data

from metrics import test_hash_function
from sponge import sponge_factory

permute_hash = sponge_factory(mixing_subroutine=permutation, 
                              output_size=16, rate=16, capacity=20)

#import sys
#with open("phtest.txt", "w") as _file:                              
#    backup = sys.stdout
#    sys.stdout = _file
#    test_hash_function(permute_hash)
#    sys.stdout = backup
#    _file.flush()
test_hash_function(permute_hash)