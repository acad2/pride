def permute(left_byte, right_byte, key_byte):        
    """ Psuedorandom function. left_byte, right_byte, and key_byte are all
        16-bit unsigned integers. 
        
        psuedo code:
            
            right_byte += key_byte + 1
            left_byte += right_byte >> 8
            left_byte ^= rotate_right(right_byte, 3)
            
        The basic idea is to view the left and right bytes as two wheels on a 
        simple combination lock. The right wheel is incremented by an amount,
        and if the amount "wraps around", then the left wheel is incremented
        by an amount as well. For example:
            
            [(0, 0), (0, 1), (0, 2), (0, 3), ... (0, 8), (0, 9), (1, 0), (1, 1), ...]
            
        The "wrap around" effect is achieved via overflow into the high order 
        byte instead of addition modulo 256. 
        
        After the overflow is added to the left byte, the right byte is rotated
        by an amount and combined with the left via bitwise exclusive or. This
        helps add nonlinearity to the transformation. 
        
        Two rounds are required to achieve full diffusion. """                
        
    right_byte = (right_byte + key_byte + 1) & 65535
    left_byte = (left_byte + (right_byte >> 8)) & 65535
    left_byte ^= ((right_byte >> 3) | (right_byte << (16 - 3))) & 65535
    return left_byte, right_byte
    
def permute_subroutine(data, key, index):    
    """ Helper function """
    data[index - 1], data[index] = permute(data[index - 1], data[index], key[index])
    
def crypt_data(data, key, tag, rounds=3):        
    """ Feistel network based which uses permute as the round function.
        Functions as a basic feistel network, with some extra details:
            
            - The round function is applied on two bytes at a time, as they are loaded into the buffer
                - Two permute calls happen: one on the "right" buffer, and one on the key
                    - The "right" buffer is permuted with the key                    
                    - The key is permuted with the "right" buffer
            - The key is permuted with itself
            - The right is permuted with the key, and the left xor-d with the right
                - Happens with one byte at a time; One is permuted, the data is crypted and tag is updated
                    - The low order byte is key material
                    - The high order byte is tag material 
            - The halves are swapped as in a standard Feistel Network
            
        The cipher is an involution. This means that Encrypt(Encrypt(Message)) == Message.
        As a result less code is required.
        
        The key schedule is online and requires no up front preprocessing.

        Encryption produces an authentication tag, regardless of the mode of
        operation used. """
    size = len(data)
    half_size = size / 2
    assert len(key) == half_size
    last_byte_of_right = half_size - 1
    
    right = [0 for index in range(half_size)] # buffer of 16-bit wide unsigned integers  
    master_key = list(key)
    key = master_key[:]
    
    for round in range(rounds):         
        key = master_key[:]
        
        # load bytes into the "right" buffer while permuting them and the key           
        right[last_byte_of_right] = data[size - 1]        
        right[last_byte_of_right - 1] = data[size - 2]
        
        permute_subroutine(right, key, last_byte_of_right)
        
        for index in reversed(range(half_size - 1)):                         
            # load next byte into buffer
            right[index - 1] = data[half_size + index] 

            # permute "right" buffer with key            
            # permute key with "right" buffer
            permute_subroutine(right, key, index)                                                                    
            permute_subroutine(key, right, index)
                
        for index in reversed(range(half_size)): # permute key again; ensures complete diffusion
            permute_subroutine(key, key, index)
                
        # permute the entire right buffer again and xor one byte at a time into data/tag, and then swap left/right                        
        for index in reversed(range(half_size)): 
            # permute the "right" buffer with the key
            permute_subroutine(right, key, index)            
                        
            key_byte = right[index] # a 16 bit word
            tag[index] ^= key_byte >> 8 # the high order byte is the tag
            data[index] ^= key_byte & 255 # the low order byte is the data
            data[index], data[half_size + index] = data[half_size + index], data[index] # swap the halves
            
    for index in range(half_size):
        data[index], data[half_size + index] = data[half_size + index], data[index]                 
    
import pride.crypto

class Feistel_Cipher(pride.crypto.Cipher):
        
    def __init__(self, *args):
        super(Feistel_Cipher, self).__init__(*args)
        self.blocksize = 16
        
    def encrypt_block(self, plaintext, key, tag):            
        #assert tag
        data = list(plaintext)
        assert isinstance(key, bytearray)
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
    crypt_data(data, key, tag, 5)
    print data, tag
    crypt_data(data, key, tag, 5)
    _data, _tag = data[:], tag[:] 
    collisions = []
    #for index in range(len(data)):
    index = 0
    for other_value in range(256):
        print other_value, len(collisions)
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
    #crypt_data_test()
    Feistel_Cipher.test_encrypt_decrypt([0 for number in range(16)], "ofb")
    Feistel_Cipher.test_metrics([0 for number in range(16)], "\x00" * 16, mode="ofb")
    
    #cipher = Feistel_Cipher([0 for number in range(16)], "ecb")
    #tag = [0] * 4
    #ciphertext = cipher.encrypt(("\x00" + "Message ") * 2, "\x00" * 16, tag)
    #print ciphertext, tag
    #ciphertext2 = cipher.encrypt(ciphertext, "\x00" * 16, tag)
    #print ciphertext2, tag
    #print cipher.encrypt(ciphertext2, "\x00" * 16, tag), tag