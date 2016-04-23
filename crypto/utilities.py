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