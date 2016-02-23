from os import urandom
from utilities import slide
from ciphertest import S_BOX, xor_sum

bytes1 = urandom(512)
bytes2 = urandom(512)

runs = []
_indices = []
max_run = 2
for index, byte in enumerate(bytes1):
    if byte in bytes2:
        _index = bytes2.index(byte)
        run = []        
        try:
            while bytes2[_index] == bytes1[index]:                     
                run.append(bytes2[_index])
                _index += 1
                index += 1
        except IndexError:
            pass
            
        if len(run) >= max_run:
            runsize = len(run)
            _indices.append(_index - runsize)
            #print _index - runsize, _index, bytes2[_index - runsize:_index]
            runs.append(''.join(run))
            max_run = len(run)
print runs       
for run in runs:
    print run
    
    
#print bytes1
#print bytes2 
assert runs     
def crypt_bytes(byte_string):    
    crypted_bytes = []       
    for byte_pair in slide(byte_string, 2):
        data = bytearray(byte_pair)
        crypted_bytes.append(data[0] ^ data[1])
        print data[0], data[1]
    return crypted_bytes
    #crypt_block(data)
    #crypted_bytes.append(bytes(data[0]))
crypted_bytes1 = crypt_bytes(bytes1)
crypted_bytes2 = crypt_bytes(bytes2)
matches = []
for _index, byte in enumerate(crypted_bytes1):
    for index, byte2 in enumerate(bytearray(bytes2[_index + 1:])):
        if byte ^ byte2 == bytes2[index - 1]:
            matches.append((byte ^ byte2, byte2))
            
print matches

