import hashutilities
import hashlib

hash_function = hashutilities.HMAC_SHA256

def crack_password_hash(password_hash, hash_function, dictionary=hashutilities.RANGE_256,
                        joiner='', max_length=6):
    if hash_function('', '') == password_hash:
        # found a blank password. On the upside, users who choose bad passwords save you cpu cycles
        return ''
        
    for length in range(1, max_length):
        test_guesses = [dictionary for byte in range(length)]
        try:
            return hashutilities.brute_force(password_hash, hash_function, test_guesses, '', joiner=joiner)
        except ValueError:
            continue
    raise ValueError("Unable to recover password with given configuration")
    
def test_crack_password_hash():     
    blank_password_hash = hash_function('', '')
    blank_password = crack_password_hash(blank_password_hash, hash_function)
    assert blank_password == ''
    
    password = "This is a test password"
    guesses = ["ella", "lacey", "this", "is", "a", "test", "password", "12345", "1111"]
    for word in guesses[:]:
        uppercase_word = word[0].upper() + word[1:]
        if uppercase_word != word:
            guesses.append(uppercase_word)
    password_hash = hash_function('', password)
    recovered_password = crack_password_hash(password_hash, hash_function, dictionary=guesses, joiner=' ')
    assert recovered_password == password, (recovered_password, password)
            
if __name__ == "__main__":
    test_crack_password_hash()
    