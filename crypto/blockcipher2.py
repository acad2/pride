from utilities import generate_s_box, xor_sum

S_BOX = generate_s_box(lambda counter: pow(251, counter, 257) % 256)

def crypt_bytes(data, key, state, index, direction):
    new_state = 0
    for offset in range(len(data)):        
        data[index], key[index] = key[index], data[index]
        
        key_byte = key[index] = S_BOX[S_BOX[data[index]] ^ S_BOX[index] ^ state]  
        new_state ^= key_byte
        
        index += direction
    return new_state
    
def decrypt_bytes(data, final_key, state):
    new_state = 0
    for index, key_byte in enumerate(final_key):
        state ^= key_byte
        
        
    
def test_crypt_bytes():
    message = bytearray("\x00" * 8)#Testing!")
    key = bytearray("\x00" * 8)
    state = 0
    for round in range(4):
      #  print "Next round; New key:"
        state = crypt_bytes(message, key, state, 0, 1)
        print "\nMessage: ", len(message), message
        
    state = xor_sum(message)
    end_of_message = len(message) - 1
    for round in range(4):
        state = crypt_bytes(message, key, state, end_of_message, -1)
        print "\nMessage: ", len(message), message
        
if __name__ == "__main__":
    test_crypt_bytes()