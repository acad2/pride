import string

import mpre.base

PLAINTEXT_KEY = string.ascii_lowercase
POLYBIUS_SQUARE = [chr(x) for x in xrange(65, 90)] # capital ascii letters
POLYBIUS_SQUARE[-1] = 'YZ'

MORSE_CODE = {".-" : 'a',
              "-..." : 'b',
              "-.-." : 'c',
              "-.." : 'd',
              "." : 'e',
              "..-." : 'f',
              "--." : 'g',
              "...." : 'h',
              ".." : 'i',
              ".---" : 'j',
              "-.-" : 'k',
              ".-.." : 'l',
              "--" : 'm',
              "-." : 'n',
              "---" : 'o',
              ".--." : 'p',
              "--.-" : 'q',
              ".-." : 'r',
              "..." : 's',
              "-" : 't',
              "..-" : 'u',
              "...-" : 'v',
              ".--" : 'w',
              "-..-" : 'x',
              "-.--" : 'y',
              "--.." : 'z',
              ".-.-.-" : '.',
              "--..--" : ',',
              "..--.." : '?',
              "-..-." : '/',
              ".--.-." : '@',
              ".----" : '1',
              "..---" : '2',
              "...--" : '3',
              "....-" : '4',
              "....." : '5',
              "-...." : '6',
              "--..." : '7',
              "---.." : '8',
              "----." : '9',
              "-----" : '0'}

BACON_CIPHER = {"AAAAA" : 'a',
                "AABBA" : 'g',
                "ABBAA" : 'n',
                "BAABA" : 't',
                "AAAAB" : 'b',
                "AABBB" : 'h',
                "ABBAB" : 'o',
                "BAABB" : 'u',
                "BAABB" : 'v',
                "AAABA" : 'c',
                "ABAAA" : 'i',
                "ABAAA" : 'j',
                "ABBBA" : 'p',
                "BABAA" : 'w',
                "AAABB" : 'd',
                "ABAAB" : 'k',
                "ABBBB" : 'q',
                "BABAB" : 'x',
                "AABAA" : 'e',
                "ABABA" : 'l',
                "BAAAA" : 'r',
                "BABBA" : 'y',
                "AABAB" : 'f',
                "ABABB" : 'm',
                "BAAAB" : 's',
                "BABBB" : 'z'}
 
POLYBIUS_TABLE = ['A', 'B', 'C', 'D', 'E',
                  'F', 'G', 'H', 'I', 'J',
                  'K', 'L', 'M', 'N', 'O',
                  'P', 'Q', 'R', 'S', 'T',
                  'U', 'V', 'W', 'X', 'YZ']
   
ADFGVX_TABLE = ['8', 'p', '3', 'd', '1', 'n',
                'l', 't', '4', 'o', 'a', 'h',
                '7', 'k', 'b', 'c', '5', 'z',
                'j', 'u', '6', 'w', 'g', 'm',
                'x', 's', 'v', 'i', 'r', '2',
                '9', 'e', 'y', '0', 'f', 'q']

ADFGVX = "adfgvx"         
DVORAK = "axje.uidchtnmbrl'poygk,qf;"
         
class Encryption_Scheme(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    
    def encrypt(self, message):
        for cipher in self.ciphers:
            message = message.encode(message)
        return message
        
    def decrypt(self, message):
        for cipher in reversed(self.ciphers):
            message = message.decode(message)
        return message
        
        
class Cipher(mpre.base.Base):
           
    defaults = mpre.base.Base.defaults.copy()
    
    def encode(self, message):
        raise NotImplementedError
        
    def decode(self, encoded_message):
        raise NotImplementedError
        
    def test(self):
        self.alert("Testing...", 0)
        
        
class Substitution_Cipher(Cipher):
        
    defaults = Cipher.defaults.copy()
    defaults.update({"plaintext_key" : PLAINTEXT_KEY,
                     "cipher_key" : DVORAK})
    
    def _get_decipher(self):
        cipher_key = self.cipher_key
        plaintext_key = self.plaintext_key
        return dict((letter, plaintext_key[cipher_key.index(letter)]) for
                     letter in cipher_key)
    decipher = property(_get_decipher)
    
    def _get_cipher(self):
        cipher_key = self.cipher_key
        plaintext_key = self.plaintext_key
        return dict((letter, cipher_key[plaintext_key.index(letter)]) for
                     letter in plaintext_key)
                     
    def _set_cipher(self, cipher):
        plaintext_key = self.plaintext_key = []
        cipher_key = self.cipher_key = []
        for key, value in cipher.items():
            plaintext_key.append(value)
            cipher_key.append(key)
    cipher = property(_get_cipher, _set_cipher)
 
    def encode(self, message):
        cipher = self.cipher
        return ''.join(cipher[character] for character in message)   
        
    def decode(self, encoded_message):
        decipher = self.decipher
        if ' ' in encoded_message:
            encoded_message = encoded_message.split()
        return ''.join(decipher[character] for character in encoded_message)
    
    def test(self):
        super(Substitution_Cipher, self).test()
        if type(self) == Substitution_Cipher:
            print self.decode("D.APY".lower())
            print self.decode("AEGNY".lower())

        
class Equidistant_Letter_Sequence(Cipher):
    
    defaults = Cipher.defaults.copy()
    defaults.update({"start" : 0,
                     "interval" : 1})
    
    def decode(self, encoded_message):
        return encoded_message[self.start::self.interval]

    def crack(self, message, dont_count_spaces=False, minimum_size=2):
        message = message.replace(' ', '') if dont_count_spaces else message
        size = len(message)
        backup = (self.start, self.interval)
        
        possibilities = []
        for start_at in xrange(0, size):
            for interval in xrange(2, size):
                self.start = start_at
                self.interval = interval
                possibilities.append(self.decode(message))
                possibilities.append(self.decode(reversed(message)))                
        return possibilities
                
    def test(self):
        super(Equidistant_Letter_Sequence, self).test()
        print self.decode("call all stikes")
        print self.decode("he took one key?")
        print self.decode("miles in reassess shall leave every sin")

        
class Array_Cipher(Cipher):
        
    defaults = Cipher.defaults.copy()
    defaults.update({"key" : POLYBIUS_SQUARE,
                     "row_length" : 5})

    def decode(self, encoded_message):
        key = self.key
        if ' ' in encoded_message:
            encoded_message = encoded_message.split()
        return ''.join(key[self.calculate_index(integer_pair)] for 
                       integer_pair in encoded_message)        
    
    def calculate_index(self, integer_pair):
        # -1 because of 0 based indexing
        row, column = int(integer_pair[0]) - 1, int(integer_pair[1]) - 1
        result = self.row_length * row + column 
        return result
        
    def test(self):
        super(Array_Cipher, self).test()
        if type(self) == Array_Cipher:
            print self.decode("33 15 45 23 35 14")
            print self.decode("13 35 34 34 15 13 45")


class Morse_Code(Substitution_Cipher):
                
    defaults = Substitution_Cipher.defaults.copy()
    defaults.update({"cipher" : MORSE_CODE})
    
    def test(self):
        super(Morse_Code, self).test()
        print self.decode(".-.. .. ..-. .")    
        print self.decode(".-. . ... .--. --- -. ... .")    
        print self.decode(". .-.. . -.-. - .-. .. -.-.")
        print self.decode("... .. -- ..- .-.. .- - --- .-.")
        print self.decode("-.-. --- ..- .-. ... .")

        
class Adfgvx_Cipher(Array_Cipher):
        
    defaults = Array_Cipher.defaults.copy()
    defaults.update({"key" : ADFGVX_TABLE})
        
    def calculate_index(self, pair):
        pair = pair.lower()
        return (ADFGVX.index(pair[0]) * 6) + ADFGVX.index(pair[1])
                
    def test(self):
        super(Adfgvx_Cipher, self).test()
        print self.decode("FF DV FG FD GV VV DG GD AX AG")    
        print self.decode("FG DV FD XD")
        print self.decode("DV VV VV DV XF")
        print self.decode("FD AX XD XD")

                     
class Bacon_Cipher(Substitution_Cipher):
        
    defaults = Substitution_Cipher.defaults.copy()
    defaults.update({"cipher" : BACON_CIPHER})
    
    def test(self):
        super(Bacon_Cipher, self).test()
        self.alert("Deciphering: {}".format(self.decipher), level=0)
        print self.decode("AABAB ABAAA BAAAA AABAA BABAA AAAAA ABABA ABABA ")
        print self.decode("BAABB BAAAA AABBA AABAA ABBAA BAABA")    

        
class Atbash_Cipher(Substitution_Cipher):
    
    defaults = Substitution_Cipher.defaults.copy()
    defaults.update({"cipher_key" : ''.join(reversed(string.ascii_lowercase)).upper()})

    def test(self):  
        super(Atbash_Cipher, self).test()
        print self.decode("GVHG")
        print self.decode("HVXFIRGB")                   

        
class Key_Rotation_Cipher(Substitution_Cipher):
            
    defaults = Substitution_Cipher.defaults.copy()
    defaults.update({"rotation_amount" : 13})
    
    def __init__(self, **kwargs):
        super(Key_Rotation_Cipher, self).__init__(**kwargs)
        self.cipher_key = self.rotate_key(self.plaintext_key, self.rotation_amount)
    
    def rotate_list_key(self, key):
        return ''.join(key.pop(0) for x in xrange(shift))
        
    def rotate_key(self, key, shift=1):
        new_key = bytearray(key + ' ')        
        for x in xrange(shift):
            new_key[-1] = new_key[-2]
            new_key = chr(new_key[-1]) + new_key[:-1]        
        return str(new_key)
      
    def test(self):
        print self.decode("sver")
        print self.decode("urneg")   

    def crack(self, encoded_message):
        old_key = plaintext_key = self.plaintext_key
        possibilities = []
        for rotation_amount in xrange(1, len(plaintext_key)):
            old_key = self.cipher_key = self.rotate_key(old_key, 1)
            possibilities.append(self.decode(encoded_message))
        return possibilities
    
    def test_crack(self):
        super(Key_Rotation_Cipher, self).test()
        print self.crack("MFH")    
        print self.crack("UPF")
        print self.crack("CBDLXBSET")
        print self.crack("BSNSFTU")
        print self.crack("FOHMBOE")        

        
if __name__ == "__main__":
    for cipher in (Substitution_Cipher, Equidistant_Letter_Sequence,
                   Array_Cipher, Morse_Code, Adfgvx_Cipher, Bacon_Cipher,
                   Atbash_Cipher, Key_Rotation_Cipher):
        print "Creating test cipher: ", cipher
        test_cipher = cipher()
        test_cipher.test()