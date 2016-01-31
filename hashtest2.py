
def autokey_function(input_data):
    data = bytearray(input_data)    
    key = (45 + sum(data)) * 2 * len(data)
    for index, byte in enumerate(data):
        prf_input = sum(data[:index] + data[index:]) + key + index
        psuedorandom_byte = pow(251, prf_input, 257) % 256
        data[index] ^= psuedorandom_byte
        key ^= index ^ psuedorandom_byte
    return bytes(data)
    
def rotate(input_string, amount):
    if not amount or not input_string:            
        return input_string    
    else:
        amount = amount % len(input_string)
        return input_string[-amount:] + input_string[:-amount]
        
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
    import binascii
    try:
        output = binascii.unhexlify(_hex[:-1 if _hex[-1] == 'L' else None])
    except TypeError:
        output = binascii.unhexlify('0' + _hex[:-1 if _hex[-1] == 'L' else None])
        
    if len(output) == len(bitstring) / 8:
        return output
    else:
        return ''.join(chr(int(bits, 2)) for bits in slide(bitstring, 8))
        
def rotation_function(input_data):
    output_data = binary_form(input_data)
    rotation_width = len(input_data)
   # output_data = bytearray(input_data)
    for index, byte in enumerate(bytearray(input_data)):
        output_data = output_data[:index * 8] + rotate(output_data[index * 8:], (index + 1) * (1 + byte))
    return byte_form(output_data)
    
def test_autokey_function():
    data = "\x00"
    outputs = [data]
    while True:
        data = autokey_function(data)
        if data in outputs:
            break
        outputs.append(data)
    print len(outputs)
    
if __name__ == "__main__":
    test_autokey_function()