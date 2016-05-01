NULL_KEY = list(0 for count in range(256))
ODD_NUMBERS = list(set(((number * 2) | 1 for number in range(256))))

def permutation(data, key):    
    for index in reversed(xrange(1, len(data))):        
        right_byte = data[index] # right_byte = 16 bit unsigned int
        right_byte += key[index] # increment, potentially overflowing low order byte
        data[index - 1] = (data[index - 1] + (right_byte >> 8)) & 255 # add any bits in high order byte to next byte
        
        right_byte &= 255 # mask to 8 bit unsigned int
        data[index] = right_byte                    
        
        data[index - 1] ^= ((right_byte >> 5) | (right_byte << (8 - 5))) & 255 # provides diffusion
        
    data[0] = (data[0] + key[0]) & 255  
    return data

def permutation(data, key):    
    size = len(data)
    for index in reversed(xrange(1, size)):        
        right_byte = data[index] # right_byte = 16 bit unsigned int
        right_byte += key[index] # increment, potentially overflowing low order byte
        data[index - 1] = (data[index - 1] + (right_byte >> 8)) & 255 # add any bits in high order byte to next byte
        
        right_byte &= 255 # mask to 8 bit unsigned int
        data[index] = right_byte                    
        
        data[index - 1] ^= ((right_byte >> 3) | (right_byte << (8 - 3))) & 255 # rotate
        
    # wrap the first byte around to the last byte
    index = 0
    right_byte = data[index] # right_byte = 16 bit unsigned int
    right_byte += key[index] # increment, potentially overflowing low order byte
    data[index - 1] = (data[index - 1] + (right_byte >> 8)) & 255 # add any bits in high order byte to next byte
    
    right_byte &= 255 # mask to 8 bit unsigned int
    data[index] = right_byte                    
    
    data[index - 1] ^= ((right_byte >> 5) | (right_byte << (8 - 5))) & 255 # provides diffusion
        
    data[0] = (data[0] + key[0]) & 255  
    return data
    
from metrics import test_hash_function, test_collisions
from sponge import sponge_factory

def _hash(data):
    key = range(len(data))
    for round in range(1):
        permutation(data, key)
       # permutation(data, key)
       
    return data
    
permute_hash = sponge_factory(mixing_subroutine=_hash, 
                              output_size=3, rate=3, capacity=0)

#import sys
#with open("phtest.txt", "w") as _file:                              
#    backup = sys.stdout
#    sys.stdout = _file
#    test_hash_function(permute_hash)
#    sys.stdout = backup
#    _file.flush()
test_collisions(permute_hash, 3)
#test_hash_function(permute_hash)