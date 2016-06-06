import os
import struct
from operator import xor as _operator_xor
import binascii

# copied from pride so this module could conceivably be used independently
def slide(iterable, x=16):
    """ Yields x bytes at a time from iterable """
    slice_count, remainder = divmod(len(iterable), x)
    for position in range((slice_count + 1 if remainder else slice_count)):
        _position = position * x
        yield iterable[_position:_position + x]         
# end copied code
    
def null_pad(seed, size):
    return bytearray(seed + ("\x00" * (size - len(seed))))
    
def xor_parity(data):
    bits = [int(bit) for bit in cast(bytes(data), "binary")]
    parity = bits[0]
    for bit in bits[1:]:
        parity ^= bit
    return parity

def xor_sum(data):
    _xor_sum = 0
    for byte in data:
        _xor_sum ^= byte
    return _xor_sum
    
def rotate(input_string, amount):
    if not amount or not input_string:            
        return input_string    
    else:
        amount = amount % len(input_string)
        return input_string[-amount:] + input_string[:-amount]                

def rotate_right(x, r, bit_width=8): 
    r %= bit_width
    return ((x >> r) | (x << (bit_width - r))) & ((2 ** bit_width) - 1)
    
def rotate_left(x, r, bit_width=8):     
    r %= bit_width
    return ((x << r) | (x >> (bit_width - r))) & ((2 ** bit_width) - 1)
    
def shift_left(byte, amount, bit_width=8):
    return (byte << amount) & ((2 ** bit_width) - 1)   
    
def shift_right(byte, amount, bit_width=8):
    return (byte >> amount) & ((2 ** bit_width) - 1)
        
def xor_subroutine(bytearray1, bytearray2): 
    size = min(len(bytearray1), len(bytearray2))
    for index in range(size):
        bytearray1[index] ^= bytearray2[index]
        
#    for index, byte in enumerate(bytearray2):
#        bytearray1[index] ^= byte  
               
def replacement_subroutine(bytearray1, bytearray2): 
    size = min(len(bytearray1), len(bytearray2))
    for index in range(size):
        bytearray1[index] = bytearray2[index]
        
    #for index, byte in enumerate(bytearray2):
    #    bytearray1[index] = byte
        
def binary_form(_string):
    """ Returns the a string representation of the binary bits that constitute _string. """
    try:
        return ''.join(format(ord(character), 'b').zfill(8) for character in _string)
    except TypeError:        
        if isinstance(_string, bytearray):
            raise
        bits = format(_string, 'b')
        bit_length = len(bits)
        if bit_length % 8:
            bits = bits.zfill(bit_length + (8 - (bit_length % 8)))                
        return bits
        
def byte_form(bitstring):
    """ Returns the ascii equivalent string of a string of bits. """
    try:
        _hex = hex(int(bitstring, 2))[2:]
    except TypeError:
        _hex = hex(bitstring)[2:]
        bitstring = binary_form(bitstring)
    try:
        output = binascii.unhexlify(_hex[:-1 if _hex[-1] == 'L' else None])
    except TypeError:
        output = binascii.unhexlify('0' + _hex[:-1 if _hex[-1] == 'L' else None])
        
    if len(output) == len(bitstring) / 8:
        return output
    else:
        return ''.join(chr(int(bits, 2)) for bits in slide(bitstring, 8))
      
def integer_form(_string):
    return int(binary_form(_string), 2)
        
_type_resolver = {"bytes" : byte_form, "binary" : binary_form, "integer" : lambda bits: int(bits, 2)}
    
def cast(input_data, _type):
    return _type_resolver[_type](input_data)
    
def hamming_weight(byte):
    # from http://stackoverflow.com/a/109025/3103584
    # "you are not meant to understand or maintain this code, just worship the gods that revealed it to mankind. I am not one of them, just a prophet"
    byte = byte - ((byte >> 1) & 0x55555555)
    byte = (byte & 0x33333333) + ((byte >> 2) & 0x33333333)
    return (((byte + (byte >> 4)) & 0x0F0F0F0F) * 0x01010101) >> 24    
    
def generate_s_box(function):
    S_BOX = bytearray(256)
    for number in range(256):    
        S_BOX[number] = function(number)        
    return S_BOX    
    
def find_cycle_length(function, *args, **kwargs):
    args = list(args)
    _input = args[0]    
    outputs = [_input]            
    while True:                        
        args[0] = function(*args, **kwargs)         
        if args[0] in outputs:            
            break
        else:
            outputs.append(args[0])
    return outputs

def find_long_cycle_length(max_size, block_size, function, _input, *args, **kwargs):
    outputs = set([bytes(_input)])
 
    blocks, extra = divmod(max_size, block_size)
    exit_flag = False
    for block in xrange(blocks if not extra else blocks + 1):        
        for counter in xrange(block_size):                           
            _input = bytes(function(bytearray(_input), *args, **kwargs))          
            if _input in outputs:  
                exit_flag = True
                break
            else:
                outputs.add(_input)
        if exit_flag:
            break                
        yield block * block_size

    yield outputs
    
def random_oracle_hash_function(input_data, memo={}):
    try:
        return memo[input_data]
    except KeyError:
        result = memo[input_data] = os.urandom(32)
        return result
        
def generate_key(size, wordsize=8):
    key_material = binary_form(os.urandom(size))
    if wordsize == 8:
        result = key_material
    else:
        result = [int(word, 2) for word in slide(key_material, wordsize)] 
    return result
    
def pad_input(hash_input, size):        
    hash_input += chr(128)
    input_size = len(hash_input) + 8 # + 8 for 64 bits for the size bytes at the end
    padding = size - (input_size % size)
    hash_input += ("\x00" * padding) + (struct.pack("Q", input_size)) 
    assert not len(hash_input) % size, (len(hash_input), size)
    return hash_input
    
def bytes_to_words(seed, wordsize):
    state = []
    seed_size = len(seed)
    for offset in range(seed_size / wordsize):        
        byte = 0
        offset *= wordsize
        for index in range(wordsize):        
            byte |= seed[offset + index] << (8 * index)
        state.append(byte)
    return state
    
def words_to_bytes(state, wordsize):        
    output = bytearray()
    storage = state[:]
    while storage:
        byte = storage.pop(0)
        for amount in range(wordsize):
            output.append((byte >> (8 * amount)) & 255)
    return output
    
def bytes_to_integer(data):
    output = 0
    size = len(data)
    for index in range(size):
        output |= data[index] << (8 * (size - 1 - index))
    return output
    
def integer_to_bytes(integer, _bytes=16):
    output = bytearray()
    #_bytes /= 2
    for byte in range(_bytes):        
        output.append((integer >> (8 * (_bytes - 1 - byte))) & 255)
    return output
    
def high_order_byte(byte, wordsize=8):
    bits = (wordsize / 2) * 8
    mask = ((2 ** bits) - 1) << bits
    return (byte & mask) >> bits
    
def low_order_byte(byte, wordsize=8):
    bits = (wordsize / 2) * 8    
    return (byte & ((2 ** bits) - 1))
    