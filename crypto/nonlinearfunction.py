from ctypes import c_uint8 as eight_bit_integer, c_uint16 as word
from utilities import cast, hamming_weight, rotate_left, rotate_right, find_cycle_length
from differential import find_best_differential #build_difference_distribution_table, find_best_output_differential
 
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
    
  
    
if __name__ == "__main__":
    #test_nonlinear_function()
    #test_nonlinear_function2()
    #test_nonlinear_function3()
    test_nonlinear_function4()
    #test_nonlinear_function5()
    