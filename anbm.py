import sys
import operator
import itertools
import collections

from utilities import convert, print_in_place

BINARY = "01"
TERNARY = "0123456789"
    
def decrement(number, base):
    def _decrement(_bytearray, index, base):
        try:
            new_value = base.index(chr(_bytearray[index])) - 1
        except IndexError:
            pass
        else:
            if chr(_bytearray[index]) == base[0]:
                _bytearray[index] = base[new_value]
                if abs(index - 1) <= len(_bytearray):
                    _decrement(_bytearray, index - 1, base)                 
            else:
                _bytearray[index] = base[new_value]            

    result = bytearray(number)
    _decrement(result, -1, base)
    return str(result)
     
def increment(number, base):
    def _increment(_bytearray, index, base):
        if chr(_bytearray[index]) == base[-1]:
            _bytearray[index] = base[0]
            if abs(index) == len(_bytearray):
                _bytearray = base[0] + _bytearray
            _increment(_bytearray, index - 1, base)
        else:
            _bytearray[index] = base[base.index(chr(_bytearray[index])) + 1]
        return _bytearray
    return str(_increment(bytearray(number), -1, base))

def query_oracle(input_data, key1=BINARY, key2=TERNARY, padding=8):
    return convert(input_data, key1, key2).zfill(padding)
    
def brute_force(symbols):
    """ Generates all possible combinations of characters in the set of symbols """   
    return itertools.permutations(symbols)
 
def crack(key1, yield_interval=100000):
    """ Recover the second key used to convert data by the oracle """
    associations = collections.OrderedDict()
    key_contents = set()
    for x in xrange(int("1" * 8, 2)):
        in_binary = format(x, 'b').zfill(8)
        converted = query_oracle(in_binary, key1)
        associations[in_binary] = converted
        key_contents.update(converted)
    
    _input, known_output = associations.popitem()
    key = bytearray(256)
    rightmost_index = 0
    counter = 0
    for possible_key in brute_force(key_contents):
        converted = query_oracle(_input, key1, possible_key)
        if converted == known_output:
            significant = False            
            for character in known_output:
                if significant or character != '0':
                    significant = True
                    index = possible_key.index(character)
                    key[index] = character
                    if index > rightmost_index:
                        rightmost_index = index
            _input, known_output = associations.popitem()
     #       print "Recovered key: ", key
     #       print "Input: ", _input
     #       print "known output: ", known_output
     #       print "test output : ", converted
            #possible_keys.append(''.join(possible_key))
        counter += 1
        if counter == yield_interval:
            yield key[:rightmost_index]
            counter = 0
        
for x in xrange(1, 16):        
    in_binary = format(x, 'b').zfill(8)
    decremented = decrement(in_binary, "01")
    assert int(decremented, 2) == x - 1
    
    incremented = increment(in_binary, "01")
    assert int(incremented, 2) == x + 1, (in_binary, incremented, x + 1)
        
for x in xrange(1, 16):
    #print "Decrementing: ", x
    decremented = decrement(str(x), "0123456789")
    assert int(decremented) == x - 1
    
 #   print "Incrementing: ", x
    incremented = increment(str(x), "0123456789")
    assert int(incremented) == x + 1, (incremented, x + 1)


test_string = "10000000"
converted = convert(test_string, BINARY, TERNARY)
#print converted
#assert format(int(converted, len(TERNARY)), 'b') == test_string, (format(int(converted, len(TERNARY)), 'b'), test_string)
   
for x in xrange(int("10000000", 2)):
    _string = format(x, 'b').zfill(8)
    incremented = increment(_string, BINARY)
    base_3 = convert(incremented, BINARY, TERNARY).zfill(8)
#    print "\nbinary : {}".format(incremented)
#    print "ternary: {}".format(base_3)
    
for possible_keys in crack(BINARY):
   # print len(possible_keys), possible_keys
    print_in_place("Possible key: " + str(possible_keys))
    