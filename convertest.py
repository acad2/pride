import itertools

from random import _urandom as random_bytes
from utilities import rotate
from additional_builtins import slide
from bff import unpack_factors, expand_seed

ascii = ''.join(chr(x) for x in range(256))

def xor(bits, state):    
    for index, byte in enumerate(slide(bits, 8)):
        try:
            state[index] ^= int(byte, 2)
        except IndexError:
            pass  
            
def convert(old_value, old_base, new_base):
    old_base_size = len(old_base)    
    old_base_mapping = dict((symbol, index) for index, symbol in enumerate(old_base))
            
    for leading_zero_count, symbol in enumerate(old_value):
        if old_base_mapping[symbol]:
            break
    zero_padding = new_base[0] * leading_zero_count
    
    decimal_value = sum((old_base_mapping[value_representation] * (old_base_size ** power) for
                         power, value_representation in enumerate(reversed(old_value))))                 
    if decimal_value:
        new_base_size = len(new_base)    
        new_value = ''
        while decimal_value > 0: # divmod = divide and modulo in one action
            decimal_value, digit = divmod(decimal_value, new_base_size)
            new_value += new_base[digit]
    return zero_padding + ''.join(reversed(new_value))  
    
def random_key(size=256):
    key = []
    while len(set(key)) < size:
        random_numbers = random_bytes(size)        
        key.extend(set(random_numbers).difference(key))
    return ''.join(key[:size])                         
        
def binary_form(_string):
    try:
        return ''.join(format(ord(character), 'b').zfill(8) for character in _string)
    except TypeError:        
        return format(_string, 'b')
 
def byte_form(bitstring):
    return ''.join(chr(int(bits, 2)) for bits in slide(bitstring, 8))
        
def reseed_state(reseed, state, state_size):  
    for index, byte in enumerate(reseed):
        state[index % state_size] ^= ord(byte)

def bits_from_state(state, key):    
    return format(unpack_factors(''.join(reversed(binary_form(bytes(state)))), 
                                 key), 'b')    
    
def test_hash(hash_input, key='', output_size=6, iterations=2): 
    input_size = str(len(hash_input))
    state = ''.join(reversed(binary_form(hash_input + input_size)))
    for round in range(iterations):
        state = binary_form(unpack_factors(state)) + binary_form(str(len(state)))    
    # without truncating the output, up to this point in the code the function is:
    # - collision free for all tested inputs (0 to 2 ** 16)
    # - all outputs have approximately half their bits as 1 or 0            
    return byte_form(state)[:output_size]
    
     #bytes_per_output = (len(state) / 8) / output_size
    #output = ''
    #for _bytes in slide(byte_form(state), bytes_per_output):
    #    output += chr(int(binary_form(_bytes), 2) % 256)
    #return output
    #return int(state, 2) # modulo a power of 2 yields the same remainder for all inputs... why?
    





    
    
def test_convert():
    data = chr(0) + chr(0) + "This is a test. This is a test. "
    _key = random_key()    
    #print data
    for key in (rotate(ascii, count) for count in range(3)): 
      #  key = random_key()
        converted = convert(data, _key, key)
        converted_back = convert(converted, key, _key)
    #    print converted
        assert data == converted_back, (len(data), len(converted_back), converted_back)
    
def test_test_hash():
    import itertools     
    from hashlib import sha1
    outputs = []
    key = []#2, 5, 3, 7, 11, 13, 17, 19, 23, 29]
    for count, possibility in enumerate(itertools.product(ascii, ascii)):
        hash_input = ''.join(possibility)        
        hash_output = test_hash(hash_input, key, 2, iterations=1)
        assert hash_output not in outputs, ("Collision", count, hash_output)
        outputs.append(hash_output)            
    #    printA
    #    print count, hash_output#, len(hash_output)
    
if __name__ == "__main__":
    #test_convert()
    test_test_hash()
    #test_pack_factors()