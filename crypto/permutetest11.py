from utilities import (rotate_left, rotate_right, bytes_to_words, 
                       words_to_bytes, high_order_byte, low_order_byte)             

def _unpack_bytes(left, right, low_byte, high_byte, half_size):
    top = (left & high_byte) >> half_size
    second = left & low_byte 
    third = (right & high_byte) >> half_size
    bottom = right & low_byte
    return top, second, third, bottom

def _print_state(left, right, message):
    low_byte = (2 ** 32) - 1
    high_byte = low_byte << 32
    
    top = (left & high_byte) >> 32
    second = left & low_byte
    third = (right & high_byte) >> 32
    bottom = right & low_byte
    print message
    print format(top, 'b').zfill(32)
    print format(second, 'b').zfill(32)
    print format(third, 'b').zfill(32)
    print format(bottom, 'b').zfill(32)
    
def permute(left, right, key, mask, bit_width):        
    right = (right + key + key + 1) & mask
    left = (left + (right >> 8)) & mask
    left ^= ((right >> 5) | (right << (bit_width - 5))) & mask 
    left, right = right, left
    return left, right          
             
def shift_rows(left, right, wordsize=8, bits=64, low_byte=(2 ** 32) - 1, high_byte=((2 ** 32) - 1) << 32):
    bits /= 2
    return (left & high_byte | 
            rotate_left(left & low_byte, 1 * wordsize, bits),
            
            (rotate_left(right & high_byte, 2 * wordsize, bits) << bits) |
            rotate_left(right & low_byte, 3 * wordsize, bits))                         
        
def mix_rows(left, right, wordsize=8, low_byte=(2 ** 32) - 1, high_byte=((2 ** 32) - 1) << 32, half_size=32, bits=64):
    top, second, third, bottom = _unpack_bytes(left, right, low_byte, high_byte, half_size)
    
    quarter_size = half_size / 2
    right_half = (2 ** quarter_size) - 1
    left_half = right_half << quarter_size

    _high_order_byte = lambda byte: high_order_byte(byte, quarter_size)
    _low_order_byte = lambda byte: low_order_byte(byte, quarter_size)        
         
    left, right = permute(_high_order_byte(top), _low_order_byte(top), second, right_half, quarter_size)
    top = (left << quarter_size) | right
    
    left, right = permute(_high_order_byte(second), _low_order_byte(second), third, right_half, quarter_size)
    second = (left << quarter_size) | right
    
    left, right = permute(_high_order_byte(third), _low_order_byte(third), bottom, right_half, quarter_size)
    third = (left << quarter_size) | right
    
    left, right = permute(_high_order_byte(bottom), _low_order_byte(bottom), top, right_half, quarter_size)
    bottom = (left << quarter_size) | right
    return (top << half_size) | second, (third << half_size) | bottom

first_byte = lambda byte: byte & ((2 ** 8) - 1)
second_byte = lambda byte: (byte & ((2 ** 16) - 1)) >> 8
third_byte = lambda byte: (byte & ((2 ** 24) - 1)) >> 16
fourth_byte = lambda byte: (byte & ((2 ** 32) - 1)) >> 24
    
def rotate_state(left, right, wordsize=8, low_byte=(2 ** 32) - 1, high_byte=((2 ** 32) - 1) << 32, half_size=32, bits=64):
    top, second, third, bottom = _unpack_bytes(left, right, low_byte, high_byte, half_size)    

    _top = (first_byte(top) << 24) | (first_byte(second) << 16) | (first_byte(third) << 8) | first_byte(bottom)
    _second = (second_byte(top) << 24) | (second_byte(second) << 16) | (second_byte(third) << 8) | second_byte(bottom)
    _third = (third_byte(top) << 24) | (third_byte(second) << 16) | (third_byte(third) << 8) | third_byte(bottom)
    _bottom = (fourth_byte(top) << 24) | (fourth_byte(second) << 16) | (fourth_byte(third) << 8) | fourth_byte(bottom)
    
    return (_top << 32) | _second, (_third << 32) | _bottom
          
def invert_rotate_state(left, right, wordsize=8, low_byte=(2 ** 32) - 1, high_byte=((2 ** 32) - 1) << 32, half_size=32, bits=64):
    top, second, third, bottom = _unpack_bytes(left, right, low_byte, high_byte, half_size)    

    _top = (fourth_byte(bottom) << 24) | (fourth_byte(third) << 16) | (fourth_byte(second) << 8) | fourth_byte(top)        
    _second = (third_byte(bottom) << 24) | (third_byte(third) << 16) | (third_byte(second) << 8) | third_byte(top)
    _third = (second_byte(bottom) << 24) | (second_byte(third) << 16) | (second_byte(second) << 8) | second_byte(top)
    _bottom = (first_byte(bottom) << 24) | (first_byte(third) << 16) | (first_byte(second) << 8) | first_byte(top)
    
    return (_top << 32) | _second, (_third << 32) | _bottom
           
def unmix_rows(left, right,  wordsize=8, low_byte=(2 ** 32) - 1, high_byte=((2 ** 32) - 1) << 32, half_size=32, bits=64):
    top, second, third, bottom = _unpack_bytes(left, right, low_byte, high_byte, half_size)
    quarter_size = half_size / 2
    right_half = (2 ** quarter_size) - 1
    left_half = right_half << quarter_size

    high_order_byte = lambda byte: (byte & left_half) >> quarter_size
    low_order_byte = lambda byte: (byte & right_half)    
    
    
    left, right = invert_permute(high_order_byte(bottom), low_order_byte(bottom), top, right_half, quarter_size)
    bottom = (left << quarter_size) | right
    
    left, right = invert_permute(high_order_byte(third), low_order_byte(third), bottom, right_half, quarter_size)
    third = (left << quarter_size) | right
    
    left, right = invert_permute(high_order_byte(second), low_order_byte(second), third, right_half, quarter_size)
    second = (left << quarter_size) | right
    
    left, right = invert_permute(high_order_byte(top), low_order_byte(top), second, right_half, quarter_size)
    top = (left << quarter_size) | right
    
    return (top << half_size) | second, (third << half_size) | bottom
    
def invert_permute(left, right, key, mask, bit_width):
    left, right = right, left
    left ^= ((right >> 5) | (right << (bit_width - 5))) & mask
    left = (mask + 1 + (left - (right >> 8))) & mask
    right = (mask + 1 + (right - key - key - 1)) & mask
    return left, right
    
def unshift_rows(left, right, wordsize=8, low_byte=(2 ** 32) - 1, high_byte=((2 ** 32) - 1) << 32, half_size=32, bits=64):
    bits /= 2
    return (left & high_byte |
            rotate_right(low_order_byte(left), 1 * wordsize, bits),
            
            (rotate_right(high_order_byte(right), 2 * wordsize, bits) << bits) |
            rotate_right(low_order_byte(right), 3 * wordsize, bits))            
    
def permutation(data, key, mask, bit_width):
    for index in reversed(range(1, len(data))):
        next_index = index - 1
        data[next_index], data[index] = permute(data[next_index], data[index], key[index], mask, bit_width) 
                
def test_invert_permute():
    left = right = key = 10
    mask = (2 ** 16) - 1
    width = 16
    left, right = permute(left, right, key, mask, width)
    left, right = invert_permute(left, right, key, mask, width)
    assert left == 10
    assert right == 10 
    
def test_unmix_rows():
    left = right = 10
    left, right = mix_rows(left, right)
    left, right = unmix_rows(left, right)
    assert left == 10
    assert right == 10
           
def test_unshift_rows():
    left = right = 10 | (10 << 32)
    _print_state(left, right, "Before: ")
    left, right = shift_rows(left, right)
    _print_state(left, right, "After:  ")
    left, right = unshift_rows(left, right)
    _print_state(left, right, "Back :  ")
    assert left == 10 | (10 << 32)
    assert right == 10 | (10 << 32)    
        
def test_shift_rows():
    left = 1
    right = 1
    low_byte = (2 ** 32) - 1
    high_byte = low_byte << 32
    
    def _print_in_binary(left, right, low_byte, high_byte):    
        print format(left & high_byte, 'b').zfill(32)
        print format(left & low_byte, 'b').zfill(32)
        print format(right & high_byte, 'b').zfill(32)
        print format(right & low_byte, 'b').zfill(32)
    
    _print_in_binary(left, right, low_byte, high_byte)
    left, right = shift_rows(left, right, wordsize=8)
    print
    _print_in_binary(left, right, low_byte, high_byte)                  
    
def test_mix_rows():
    left = (2 << 32) | 2
    right = (1 << 32) |  1
    low_byte = (2 ** 32) - 1
    high_byte = low_byte << 32
        
    _print_state(left, right, "Before: ")     
    left, right = mix_rows(left, right, 8)
    _print_state(left, right, "After: ")
        
def test_shift_and_mix():
    left = right =  (1 << 8) | 1
    lefts, rights = [], []
    from utilities import integer_to_bytes
    _print_state(left, right, "Before: ")
    for round in range(65536):
        left, right = shift_rows(left, right)             
        left, right = mix_rows(left, right)
     #   _print_state(left, right, "After: ")
        if left in lefts:
            if right in rights:
                break
        else:
            lefts.append(left)
        if right not in rights:
           rights.append(right)
    print len(lefts), len(rights)
    
def test_rotate_state():
    left = right = 10
    _print_state(left, right, "Before rotating: ")
    weight = lambda left, right: format(left, 'b').zfill(32).count('1') + format(right, 'b').zfill(32).count('1')
    _weight = weight(left, right)
    for round in range(4):
        left, right = rotate_state(left, right)
        assert weight(left, right) == _weight
        _print_state(left, right, "After rotating: ")
        
def test_invert_rotate_state():
    left = right = 10
    left, right = rotate_state(left, right)
    left, right = invert_rotate_state(left, right)
    assert left == 10
    assert right == 10
    
def _find_permute_cycle_length(max_size, block_size, function, left, right, key, mask, bit_width):
    recycle_point =(left, right)
    count = 0
    blocks, extra = divmod(max_size, block_size)
    exit_flag = False
    for block in xrange(blocks if not extra else blocks + 1):        
        for counter in xrange(block_size):                           
            _input = left, right = function(left, right, key, mask, bit_width) 
          #  print _input
            if _input == recycle_point:  
                exit_flag = True                
                break
            else:
                count += 1
                
        if exit_flag:
            break                
        yield count

    yield count
        
def _find_permutation_cycle_length(max_size, block_size, function, _input, key, mask, bit_width):
    recycle_point = set()     
    blocks, extra = divmod(max_size, block_size)
    exit_flag = False
    for block in xrange(blocks if not extra else blocks + 1):        
        for counter in xrange(block_size):                           
            function(_input, key, mask, bit_width) 
            __input = bytes(_input)
           # print __input
            if __input in recycle_point:  
                exit_flag = True                
                break
            else:                           
                recycle_point.add(__input)
                
        if exit_flag:
            break                
        yield len(recycle_point)
        
    yield len(recycle_point)
    yield recycle_point
    
def test_permute():    
    for progress in _find_permute_cycle_length((2 ** 16), 1024, permute, 0, 0, 1, (2 ** 16) - 1, 16):
        print progress
        
def test_permutation():
    size = 2
    bits = size * 8
#    for test in range(16):
    for progress in _find_permutation_cycle_length((2 ** bits), 1024, permutation, list(bytearray("\x00" * size)), generate_key(size), (2 ** bits) - 1, bits):
        if isinstance(progress, int):
            print progress
            
if __name__ == "__main__":
    #test_permute()
    #test_permutation()    
    #test_shift_rows()
    #test_unshift_rows()    
    #test_mix_rows()
    #test_unmix_rows()
    #test_shift_and_mix()
    #test_invert_permute()        
    test_rotate_state()
    test_invert_rotate_state()
    