def permute(left_byte, right_byte, key_byte):        
    right_byte = (right_byte + key_byte + 1) & 65535
    left_byte = (left_byte + (right_byte >> 8)) & 65535
    left_byte ^= ((right_byte >> 3) | (right_byte << (16 - 3))) & 65535
    return left_byte, right_byte
    
def crypt_data(data, key, tag, rounds=3):        
    """ Feistel network based which uses permute as the round function.
        Functions as a basic feistel network, with some extra details:
            
            - The "right" buffer is one byte longer then half the block; size(right_buffer) = (n/2) + 1
                - A round constant is loaded into this "extra" slot in the buffer
                    - This serves to modify the output of the round function and is otherwise ignored
            - The round function is applied on two bytes at a time, as they are loaded into the buffer
                - Three permute calls happen: one on the "right" buffer, and one on the left and right sides of the key
                    - The "right" buffer is permuted with the key
                    - The right half of the key is permuted with the right half of the plaintext data
                    - The left half of the key is permuted with the "right" buffer
            - The key is permuted 
            - The right is permuted with the key, and the left xor-d with the right
                - Happens with one byte at a time; One is permuted, the data is crypted and tag is updated
                    - The low order byte is key material
                    - The high order byte is tag material 
            - The halves are swapped as in a standard Feistel Network
            
        The cipher is an involution. This means that Encrypt(Encrypt(Message)) == Message.
        As a result less code is required.
        
        The key schedule is online and requires no up front preprocessing.

        Encryption produces an authentication tag"""
    half = len(data) / 2
    last_byte = half
    
    right = [0 for index in range(half + 1)] # buffer of (size + 1) 16-bit wide unsigned integers  
    master_key = list(key)
    
    for round_constant in range(rounds):  
        key = master_key[:] 
            
        # load bytes into the "right" buffer while permuting them and the key
        # first, set the "extra" rightmost byte of the buffer to the round constant and permute
        right[last_byte - 1], right[last_byte] = permute(data[-1], 1, key[last_byte - 1])#round_constant, key[last_byte - 1])        
        for index in reversed(range(half)):                         
            # load next byte into buffer
            right[index - 1] = data[half + index] 

            # permute "right" buffer with key
            right[index - 1], right[index] = permute(right[index - 1], right[index], key[index]) 
                
            # permute right half of key with right half of plaintext block
            key[(half + index) - 1], key[half + index] = permute(key[(half + index) - 1], key[half + index], data[half + index])
            
            # permute left half of key with "right" buffer
            key[index - 1], key[index] = permute(key[index - 1], key[index], right[index])
        
        for index in range(len(key)): # permute key again; ensures complete diffusion
            key[index - 1], key[index] = permute(key[index - 1], key[index], key[index])
    
        # permute the entire right buffer again and xor one byte at a time into data/tag, and then swap left/right        
        right[last_byte - 1], right[last_byte] = permute(right[last_byte - 1], right[last_byte], key[last_byte])
        for index in reversed(range(half)): 
            # permute the "right" buffer with the key
            right[index - 1], right[index] = permute(right[index - 1], right[index], key[index])
                        
            key_byte = right[index] # a 16 bit word
            tag[index] ^= key_byte >> 8 # the high order byte is the tag
            data[index] ^= key_byte & 255 # the low order byte is the data
            data[index], data[half + index] = data[half + index], data[index] # swap the halves
            
    for index in range(half):
        data[index], data[half + index] = data[half + index], data[index]                 
    
import pride.crypto

class Feistel_Cipher(pride.crypto.Cipher):
        
    def __init__(self, *args):
        super(Feistel_Cipher, self).__init__(*args)
        self.blocksize = 8
        
    def encrypt_block(self, plaintext, key, tag):            
        assert tag
        data = list(plaintext)
        crypt_data(data, [key[index] | (key[index + 1] << 8) for index in range(0, len(key), 2)], tag)        
        for index, byte in enumerate(data):
            plaintext[index] = byte        
        
    def decrypt_block(self, ciphertext, key, tag):
        self.encrypt_block(ciphertext, key, tag)
    
    
def crypt_data_test():
    data = [0, 0, 0, 0]
    tag = [0, 0]
    key = [0, 0, 0, 0]#generate_key(8, wordsize=16)
    crypt_data(data, key, tag, 5)#, 0, 1)    
    print data, tag
    _data, _tag = data[:], tag[:] 
    collisions = []
    for index in range(len(data)):        
        for other_value in range(256):
            for second_other_value in range(256):
                for third_other_value in range(256):
                    data = _data
                    data[index] = other_value
                    data[(index + 1) % len(data)] = second_other_value
                    data[(index + 2) % len(data)] = third_other_value
                    crypt_data(data, key, tag, 5)
                    if tag == _tag:
                        collisions.append((index, _data[index], _data[(index + 1) % 4], other_value, second_other_value))
    print collisions            
    #crypt_data(data, key, tag)#, 3, -1)
    #print data, tag
    
    #key = [0, 0, 0, 1]
    #tag = [0, 0]
    #crypt_data(data, key, tag)
    ##print data, tag
    #crypt_data(data, key, tag)
    ##print data, tag
        
if __name__ == "__main__":  
    #permute_test()
    crypt_data_test()
    #Feistel_Cipher.test_metrics([0 for number in range(16)], "\x00" * 16, mode="cbc", avalanche_test=False, randomness_test=False, bias_test=False)
    ##Feistel_Cipher.test_encrypt_decrypt([0 for number in range(16)], "cbc")
    #cipher = Feistel_Cipher([0 for number in range(16)], "ecb")
    #tag = [0] * 4
    #ciphertext = cipher.encrypt(("\x00" + "Message ") * 2, "\x00" * 16, tag)
    #print ciphertext, tag
    #ciphertext2 = cipher.encrypt(ciphertext, "\x00" * 16, tag)
    #print ciphertext2, tag
    #print cipher.encrypt(ciphertext2, "\x00" * 16, tag), tag