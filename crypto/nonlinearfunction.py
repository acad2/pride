import os

from ctypes import c_uint8 as eight_bit_integer, c_uint16 as word
from utilities import cast, hamming_weight, rotate_left, rotate_right, find_cycle_length
from differential import find_best_differential
from linear import calculate_linearity
 
def nonlinear_function(byte, constant):     
    byte ^= constant
    state = (byte + 1) % 256
    byte ^= eight_bit_integer(state << 5).value
    byte ^= eight_bit_integer(state >> 3).value             
    return byte
        
def nonlinear_function2(state_and_constant):
    state, constant = state_and_constant
    state ^= constant        
    state += 1    
    state ^= word(state >> 8).value        
    state ^= word(state << 8).value
    state = word(~state).value
  #  state ^= word(state << 5).value
  #  state ^= word(state >> 3).value
    
    
    return (eight_bit_integer(state).value, state)
        
def nonlinear_function3(data, mask=1 << 7):     
  #  data ^= 1 << (data % 8)
    for bit_number in range(8):    
        other_bits = (data ^ (data & (1 << bit_number))) % 2
        weight = hamming_weight(other_bits)
        data ^= other_bits << bit_number    
       
        data = (data + (other_bits + weight)) % 256
        data ^= 1 << (data % 8)
    
    return data
    
def nonlinear_function4(byte):   
    
    state = 0
    for bit in range(8):
        state ^= rotate_right(byte & rotate_left(1, bit), bit)                
             
    for bit in range(4):                        
        byte ^= rotate_left(state, bit)                  
        state ^= rotate_right(byte & rotate_left(1, bit), bit)
    
    byte = rotate_left(byte, 6)
    return byte
    
def nonlinear_function5(byte, key=6): 
    raise NotImplementedError
    #print "Function enter"
    for offset, bit in enumerate(reversed(range(1, 8))):
        random_bit = key & (bit - 1)
        shift_amount = bit - random_bit
        #print format(byte, 'b').zfill(8), bit, random_bit
        byte ^= ((1 << offset) & byte) << shift_amount
        #print format(byte, 'b').zfill(8), format(((1 << offset) & byte) << shift_amount, 'b').zfill(8)
        byte ^= ((1 << shift_amount) & byte) >> shift_amount
        #print format(byte, 'b').zfill(8), format(((1 << shift_amount) & byte) >> shift_amount, 'b').zfill(8)
        byte ^= ((1 << offset) & byte) << shift_amount
        #print format(byte, 'b').zfill(8)
                                  
    return byte

def nonlinear_function6(byte, keys):
    left = byte >> 4
    right = byte & 15
        
    for round in range(4):
        key = keys[round]
        right = (right + key) & 255
        left = (left + (right >> 4)) & 15
        left ^= rotate_left(right, 3)
        right, left = left, (right & 255)        
        
    return ((left ^ right) ^ ((left + right) & 255) + right) & 255
        
def pbox(word):
    binary_word = cast(word, "binary")
    return int(''.join(binary_word[offset::8] for offset in range(8)), 2)
        
def nonlinear_function7(left_byte, right_byte, key_byte):    
    modifier = left_byte ^ right_byte ^ key_byte
    for round in range(4):        
    #    right_byte = pbox(right_byte)
    #    left_byte = pbox(left_byte)
        modifier ^= right_byte
        right_byte = (right_byte + key_byte + modifier) & 65535
        modifier ^= right_byte ^ left_byte
        left_byte = (left_byte + (right_byte >> 8)) & 65535
        left_byte ^= ((right_byte >> 3) | (right_byte << (16 - 3))) & 65535
        modifier ^= left_byte
        
        left_byte, right_byte = right_byte, left_byte
                
    return left_byte, right_byte
    
def nonlinear_function8(left, right, key, mask=(2 ** 64) - 1, bit_width=64, _rotation=5):    
    diffuser = ((left ^ right) + key) & mask
        
    for round in range(5):                
        diffuser ^= right
        
        right = (right + key + diffuser) & mask
        
        diffuser ^= right ^ left        
        
        left = (left + (right >> 8)) & mask        
        left ^= ((right >> _rotation) | (right << (bit_width - _rotation))) & mask
        diffuser ^= left
        
        left, right = right, left        
        diffuser = (diffuser + key) & mask
        
    return left, right
    
def test_nonlinear_function():
    cycle = find_cycle_length(nonlinear_function, 235, 131)
    print len(cycle), sorted(cycle)
    
    sbox = bytearray(nonlinear_function(byte, 131) for byte in range(256))
    print find_best_differential(sbox)
    
def test_nonlinear_function2():
    cycle = find_cycle_length(nonlinear_function2, (0, 131))
    print len(cycle), cycle
    
    sbox = dict((byte, nonlinear_function2((byte, 131))[0]) for byte in range(256))  
    find_best_differential(sbox)
    
def test_function(sbox, function, *args, **kwargs):
    cycle = find_cycle_length(function, *args, **kwargs)
    print len(cycle), sorted(cycle)
    print find_best_differential(sbox)    
    
def test_nonlinear_function3():
    sbox = bytearray(nonlinear_function3(byte) for byte in range(256))
    test_function(sbox, nonlinear_function3, 1)   
        
def test_nonlinear_function4():          
    cycle = find_cycle_length(nonlinear_function4, 1)
    print len(cycle), set(range(256)).difference(cycle), cycle
    sbox = bytearray(nonlinear_function4(index) for index in range(256))
    print find_best_differential(sbox)
    
            
def test_nonlinear_function5():    
    cycle = find_cycle_length(nonlinear_function5, 1)
    print len(cycle), set(range(256)).difference(cycle), cycle
    sbox = bytearray(nonlinear_function4(index) for index in range(256))
    print find_best_differential(sbox)
    
def test_nonlinear_function6():
    import os    
    for key in range(1, 256):        
        sbox = bytearray(nonlinear_function6(right, [pow(251, x, 257) % 256 for x in range(key, key + 5)]) for right in range(256))
        print find_best_differential(sbox)
    
def test_nonlinear_function7():        
    for key in (pow(251, x, 257) % 256 for x in range(1, 256)):
        sbox = bytearray()
        for right in range(256):            
            left = 0
            left, right = nonlinear_function7(left, right, key)                                        
            sbox.append((right >> 8) ^ (right & 255))
        print find_best_differential(sbox)
    
def test_nonlinear_function8():        
    #for _rotation in range(20):
    #    print "\nRotation: ", _rotation
    #     
    for key in range(1, 3):
        sbox = bytearray()
        for right in range(256):
            left = 0
            left, right = nonlinear_function8(left, right, key)
            sbox.append(left >> 56)
        
        differentials = find_best_differential(sbox)
        linearity = calculate_linearity(sbox)        
        print differentials
        print linearity
            
def test_random_sbox():
    for x in range(16):
        sbox = bytearray(os.urandom(256))
        print find_best_differential(sbox)
        print calculate_linearity(sbox)
    
if __name__ == "__main__":
    #test_nonlinear_function()
    #test_nonlinear_function2()
    #test_nonlinear_function3()
    #test_nonlinear_function4()
    #test_nonlinear_function5()
    #test_nonlinear_function6()
    #test_nonlinear_function7()
    test_nonlinear_function8()
    #test_random_sbox()