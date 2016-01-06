from math import sqrt, ceil

import pride


BYTES = ''.join(chr(x) for x in xrange(256))

def n_dimensional_list(n):
    return [[[] for i in range(n)] for i in range(n)]

def dimensionify(bytestring, n):
    dimensions = n_dimensional_list(n)
    size = int(ceil(sqrt(len(bytestring))))
    for count in range(n - 2):
        size /= 2
    
    for bytes in slide(bytestring, size):
        _new_list = nested_list(n - 1)

x = [[0, 1, 2 , 3 ], [4 , 5 , 6 , 7 ], 
     [8, 9, 10, 11], [12, 13, 14, 15]]

x = [[[0, 1], [2, 3]], [[4, 5], [6, 7]], 
     [[8, 9], [9, 10]], 
     [[10, 11], [12, 13]],
     [[14, 15]]]

# x[0][1][2] # 3
# x[1][0][0] # 4
# x[4][0][1] # 15
        
        
def nested_list(count):
    _list = []
    for x in xrange(count):
        _list.append([])
    return _list


        
    
    
def rotate(input_string, amount):
    if not amount or not input_string:
        return input_string    
    else:
        amount = amount % len(input_string)
      #  if amount > input_size:
      #      print "Rotating by: ", len(input_string), amount, divmod(len(input_string), amount)
      #      amount, extra = divmod(len(input_string), amount)
      #      amount = amount + 1 if extra else extra
    #    print "Calculated amount: ", amount
        return input_string[-amount:] + input_string[:-amount]
    #return input_string

_XOR = {b"00" : b'0', b'01': b'1', b'10' : b'1', b'11' : b'0'}
    
def xor_bits(byte):
    result = ''
    counter = 0
    while counter < len(byte):
        try:
            result += _XOR[byte[counter:counter + 2]]
        except KeyError:
            pass
        counter += 1
   #     print result[-1]
    return result
    #return ''.join(_XOR[bits] for bits in slide(byte, 2))    
        
def permutation1(input_bytes):    
    state = BYTES    
    output_string = ''
    for character in input_bytes:
        number = ord(character)
        bits = format(number, 'b')
        
        # + * ** - %256
        
        print number, new_number
        output_string += chr(new_number)
    return output_string    
    
def one_way_permutation(input_string, output_size=0):
    output_string = ''
    state = BYTES
    for counter, character in enumerate(input_string):        
        letter_index = state.index(character)        
       # index = pow(letter_index, letter_index, 256)
       # output_string += state[index]
       # state = rotate(state, letter_index)
        index = (((letter_index * counter) + 1) % 256) ^ counter
        output_string += state[index]        
        state = rotate(state, index) # 
    return output_string
    
def auto_key_permutation(input_string, from_key=BYTES):
    output_string = ''
    key = BYTES
    for counter, character in enumerate(input_string):
        letter_index = from_key.index(character)
        output_string += key[letter_index]        
        key = rotate(key, ord(output_string[-1]))
        
    return output_string, key
    
def reverse_permutation(input_string, key, from_key=BYTES):
    output_string = ''
    counter = len(input_string)
    for character in reversed(input_string):
        key = rotate(key, -(counter + ord(character)))
        index = key.index(character)
        output_string += from_key[index]
        count -= 1
    return output_string        
        
OUTPUTS = []        
def distributed_xor(bitstring, recurse=1):    
    output = ''   
    for index, bit in enumerate(bitstring):
        for _bit in bitstring[index:]:
            output += _XOR[bit + _bit]    
    if recurse:
        recurse -= 1    
        return distributed_xor(output, recurse)
    else:
        assert output not in OUTPUTS
        OUTPUTS.append(output)
        return output
    
def betweenxor(bitstring):
    output = ''
    for index, bit in enumerate(rotate(bitstring[:-1], 0)):
        output += _XOR[bit + bitstring[index + 1]]
    return output
    
def xor_into_self(bitstring):
    output = bytearray(b"0" * 8)    
    for bit_block in slide(bitstring, 8):
        for index, bit in enumerate(bit_block):
            output[index] = _XOR[bit + chr(output[index])]
  #          print "Xoring: ", bit + chr(output[index]), _XOR[bit + chr(output[index])], str(output)
    return bytes(output)
   
def permute(bits):
  #  print "Rotating: ", int(bits, 2), int(rotate(bits, 2), 2)
    return rotate(bits, 7)
    
def xortate(bitstring, amount=3):
    return rotate(xor_into_self(distributed_xor(bitstring)), amount)
        
def xorhash(bitstring):
    _output = "10000001"
    _output += betweenxor(bitstring)
    print _output
    #for index, bit in enumerate(_output):
    #    _output[index] = _XOR[bit + chr(_output[index])]
    #bitstring = xortate(bitstring, 0)
  #  for index, bit in enumerate(bitstring):
  #      _output[index] = _XOR[bit + _output[index]]
    return xor_into_self(_output)# + bitstring)#bytes(_output)
    
    
if __name__ == "__main__":
    data = "00000011"#''.join(chr(x) for x in xrange(10))
    #print xorhash(data)
    print int(data, 2)
    for rotations in range(8):
        print int(rotate(data, rotations), 2)
    #outputs = [int(permute(format(x, 'b').zfill(8)), 2) for x in xrange(256)]
    #print len(set(outputs)), outputs
   # output = permutation1(data)
   # print "Input : ", [ord(char) for char in data]
   # print "Output: ", [ord(char) for char in output]
    #_data, key = auto_key_permutation(data)
    #print "Data : ", [ord(char) for char in data]
    #print "_Data: ", [ord(char) for char in _data]
    #print "Key: ", key