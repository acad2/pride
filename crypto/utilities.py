import binascii

# copied from pride so this module could conceivably be used independently
def slide(iterable, x=16):
    """ Yields x bytes at a time from iterable """
    slice_count, remainder = divmod(len(iterable), x)
    for position in range((slice_count + 1 if remainder else slice_count)):
        _position = position * x
        yield iterable[_position:_position + x] 
        
def save_data(*args): 
    sizes = []
    for arg in args:
        sizes.append(str(len(arg)))
    return ' '.join(sizes + [args[0]]) + ''.join(str(arg) for arg in args[1:])
    
def load_data(packed_bytes, count_or_types):
    """ Unpack a stream according to its size header.
    The second argument should be either an integer indicating the quantity
    of items to unpack, or an iterable of types whose length indicates the
    quantity of items to unpack. """
    try:
        size_count = len(count_or_types)
    except TypeError:
        unpack_types = False
        size_count = count
    else:
        unpack_types = True
    sizes = packed_bytes.split(' ', size_count)
    packed_bytes = sizes.pop(-1)
    data = []
    for size in (int(size) for size in sizes):
        data.append(packed_bytes[:size])
        packed_bytes = packed_bytes[size:]
        
    if unpack_types:
        _data = []
        for index, _type in enumerate(count_or_types):
            value = data[index]
            if _type == bool:
                value = True if value == "True" else False
            elif _type == int:
                value = int(value)
            elif _type == float:
                value = float(value)
            elif _type is None:
                value = None
            elif _type in (list, tuple, dict, set):
                value = ast.literal_eval(value)
            _data.append(value)
        data = _data
    return data 
# end copied code
    
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

def xor_subroutine(bytearray1, bytearray2):    
    for index, byte in enumerate(bytearray2):
        bytearray1[index] ^= byte  
               
def replacement_subroutine(bytearray1, bytearray2):    
    for index, byte in enumerate(bytearray2):
        bytearray1[index] = byte
        
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