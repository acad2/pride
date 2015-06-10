ASCIIKEY = ''.join(chr(x) for x in xrange(256))

def convert(old_value, old_base, new_base):
    old_base_size = len(old_base)
    new_base_size = len(new_base)
    old_base_mapping = dict((symbol, index) for index, symbol in enumerate(old_base))
    decimal_value = 0    
    new_value = ''
    
    for power, value_representation in enumerate(reversed(old_value)):
        decimal_value += old_base_mapping[value_representation]*(old_base_size**power)
                            
    if decimal_value == 0:
        new_value = new_base[0]
    else:
        while decimal_value > 0: # divmod = divide and modulo in one action
            decimal_value, digit = divmod(decimal_value, new_base_size)
            new_value += new_base[digit]

    return ''.join(reversed(new_value))
  
def get_data(filename):  
    with open(filename, 'rb') as _file:
        data = _file.read()
    return data
    
def create_file_key(data): 
    file_key = r''
    characters = set()
    for character in data:
        if character not in characters:
            file_key += character
            characters.add(character)
    return file_key
  
def binary_to_char(binary):
    string = ''
    while binary:
        string += chr(int(binary[:8], 2))
        binary = binary[8:]
    return string
    
def char_to_binary(characters):
    return ''.join(bin(ord(character))[2:] for character in characters)
        
data = get_data("base.py")  
data_base256 = convert(data, create_file_key(data), ASCIIKEY)
print len(data_base256), len(data)

bdata = '1' * (len(data_base256) + 1)
compressed = binary_to_char(bdata)       

difference = ''.join(chr(255 - ord(character)) for character in data_base256)

print len(compressed), len(difference)

_bdata = char_to_binary(compressed)
print len(_bdata), len(bdata)
assert _bdata == bdata

