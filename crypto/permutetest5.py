from utilities import pad_input

def permute(left_byte, right_byte, key_byte, modifier):        
    right_byte = (right_byte + key_byte + modifier) & 65535
    left_byte = (left_byte + (right_byte >> 8)) & 65535
    left_byte ^= ((right_byte >> 3) | (right_byte << (16 - 3))) & 65535
    return left_byte, right_byte
    
def permute_subroutine(data, key, index):   
    data[index - 1], data[index] = permute(data[index - 1], data[index], key[index], index)    
    
def permutation(data, key):        
    for round in range(2):
        for index in reversed(range(len(data))):        
            permute_subroutine(data, key, index) 
            
def permute_hash(data, rounds=2, blocksize=16):
    data = list(bytearray(pad_input(data, blocksize)))
    #data = list(bytearray((data + ("\x00" * (blocksize - len(data))))))
    for round in range(rounds):
        permutation(data, data)
    return bytes(bytearray((byte >> 8) ^ (byte & 255) for byte in data))
    
def test_permute_hash():
    data = "\x00"
    #print permute_hash(data, blocksize=2)
    from metrics import test_hash_function
    test_hash_function(permute_hash)
    
if __name__ == "__main__":
    test_permute_hash()
    