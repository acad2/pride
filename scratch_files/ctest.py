import itertools
def grouper(n, iterable, padvalue=None):
    """grouper(3, 'abcdefg', 'x') -/ ('a','b','c'), ('d','e','f'), ('g','x','x')"""
    return itertools.izip_longest(*[iter(iterable)]*n, fillvalue=padvalue)
    
def convert(old_value, old_base, new_base):
    old_base_size = len(old_base)
    new_base_size = len(new_base)
    old_base_mapping = dict((symbol, index) for index, symbol in enumerate(old_base))
    decimal_value = 0    
    new_value = ''#[]
    
    for power, value_representation in enumerate(reversed(old_value)):
        try:
            decimal_value += old_base_mapping[value_representation]*(old_base_size**power)
        except KeyError:
            print "Could not find value: ", value_representation, "in base of size: ", old_base[:128]
            assert value_representation not in old_base_mapping
            raise
                            
    if decimal_value == 0:
        new_value = new_base[0]
    else:
        while decimal_value > 0: # divmod = divide and modulo in one action
            decimal_value, digit = divmod(decimal_value, new_base_size)
            new_value += new_base[digit]

    return ''.join(reversed(new_value))
    
ASCIIKEY = ''.join(chr(x) for x in xrange(256))
key512 = ''
key1024 = ''
#key2048 = ''

for char in ASCIIKEY:
    for char1 in ASCIIKEY:
        key512 += char + char1
        #for char2 in ASCIIKEY:            
         #   key1024 += char + char1 + char2            
          #  for char3 in ASCIIKEY:
           #     key2048 += char + char1 + char2 + char3
                                
KEY512 = [symbol[0] + symbol[1] for symbol in grouper(2, key512)]
data = "I love you <3"# * 1024   
ASCIIKEY = list(set(data))
print "converting to key512"             
x = convert(data, ASCIIKEY, KEY512)
print len(data), len(x)
print "decrypting", x
_data = convert([(item[0], item[1]) for item in grouper(2, x)], #KEY512,
                [item(item[0], item[1]) for item in KEY512], 
                ASCIIKEY)
print "original data: ", data
print "decrypted: ", _data
print len(data), len(_data)
assert data == _data                                