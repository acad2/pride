from blockcipher import extract_round_key

def shuffle(data, key): 
    n = len(data)
    for i in reversed(range(1, n)):
        j = key[i] & (i - 1)
        data[i], data[j] = data[j], data[i]
        
def random_number_generator(key, first_set, output_size=256):
    extract_round_key(key)    
    key_two = key[:]
    extract_round_key(key_two)

    shuffle(first_set, key)
    second_set = first_set[:]
    shuffle(second_set, key)
    
    output_set = bytearray(256)
    while True:
        for index in range(256):
            output_set[index] = first_set[index] ^ second_set[index]
        shuffle(output_set, key)
        yield bytes(output_set[:output_size])
        shuffle(first_set, key)
        shuffle(second_set, key_two)
        
def test_random_number_generator():
    key = bytearray("\x00" * 256)
    for _bytes in random_number_generator(key, range(256), 16):
        print _bytes
        
if __name__ == "__main__":
    test_random_number_generator()
    