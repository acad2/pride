def permutation(data, key):    
    size = len(data)
    for index in reversed(xrange(1, size)):        
        right_byte = data[index] # right_byte = 16 bit unsigned int
        right_byte += key[index] # increment, potentially overflowing low order byte
        data[index - 1] = (data[index - 1] + (right_byte >> 8)) & 255 # add any bits in high order byte to next byte
        
        right_byte &= 255 # mask to 8 bit unsigned int
        data[index] = right_byte                    
        
        data[index - 1] ^= ((right_byte >> 3) | (right_byte << (8 - 3))) & 255 # rotate
        
    # wrap the first byte around to the last byte - same steps as above
    index = 0
    right_byte = data[index] 
    right_byte += key[index] 
    data[index - 1] = (data[index - 1] + (right_byte >> 8)) & 255 
    
    right_byte &= 255 
    data[index] = right_byte                    
    
    data[index - 1] ^= ((right_byte >> 5) | (right_byte << (8 - 5))) & 255             
    
from sponge import sponge_factory

def _hash(data):
    key = range(len(data))    
    for round in range(1):
        permutation(data, key)             
    return data
    
permute_hash = sponge_factory(mixing_subroutine=_hash, 
                              output_size=4, rate=4, capacity=1)

if __name__ == "__main__":
    from metrics import test_hash_function
    test_hash_function(permute_hash)
    