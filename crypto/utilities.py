import binascii

def rotate(input_string, amount):
    if not amount or not input_string:            
        return input_string    
    else:
        amount = amount % len(input_string)
        return input_string[-amount:] + input_string[:-amount]
                
def slide(iterable, x=16):
    """ Yields x bytes at a time from iterable """
    slice_count, remainder = divmod(len(iterable), x)
    for position in range((slice_count + 1 if remainder else slice_count)):
        _position = position * x
        yield iterable[_position:_position + x] 
        
def binary_form(_string):
    """ Returns the a string representation of the binary bits that constitute _string. """
    try:
        return ''.join(format(ord(character), 'b').zfill(8) for character in _string)
    except TypeError:        
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
        
_type_resolver = {"bytes" : byte_form, "binary" : binary_form, "int" : lambda bits: int(bits, 2)}
    
def cast(input_data, _type):
    return _type_resolver[_type](input_data)