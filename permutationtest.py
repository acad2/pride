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
 #   print "Rotating by: ", amount
    return input_string[-amount:] + input_string[:-amount]

_XOR = {"00" : '0', '01': '1', '10' : '0', '11' : '0'}
    
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
    
for x in xrange(16):
    bits = format(x, 'b')
    print bits, xor_bits(bits)
    
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
        
if __name__ == "__main__":
    data = ''.join(chr(x) for x in xrange(10))
   # output = permutation1(data)
   # print "Input : ", [ord(char) for char in data]
   # print "Output: ", [ord(char) for char in output]
    #_data, key = auto_key_permutation(data)
    #print "Data : ", [ord(char) for char in data]
    #print "_Data: ", [ord(char) for char in _data]
    #print "Key: ", key