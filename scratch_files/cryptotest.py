import pprint
import random
import itertools

ASCII = ''.join(chr(x) for x in xrange(256))

class Bijection(object):
    # maps a symbol to another set of symbols, where each element
    # of the domain (keys) maps to one element of the codomain (values)
    # put simply: a python dictionary that maps unique keys to unique values  

    def _get_key(self):
        return next(self._keys)
    key = property(_get_key)
    
    def _get_decryption_key(self):
        return next(self._decryption_keys)
    decryption_key = property(_get_decryption_key)
    
    def __init__(self, keys=tuple()):
        if not keys:
            raise ValueError("No keys passed to Bijection.__init__")
        self._keys = itertools.cycle(keys)
        self._decryption_keys = itertools.cycle([self.invert_key(key) for
                                                 key in keys])
        
    def invert_key(self, key):
        inverted_key = dict((value, _key) for _key, value in key.items())
        return inverted_key
        
    def apply(self, _set):
        return ''.join(self.key[element] for element in _set)
    
    def reverse(self, _set):        
        return ''.join(self.decryption_key[element] for element in _set)
        
 
class Permutation(Bijection):
    """ Maps elements of a set to other elemnts of the same set. """
    
    @staticmethod
    def create_key(_set):
        values = list(_set)
        random.shuffle(values)
        return dict((element, values[index]) for 
                     index, element in enumerate(_set))
        
  
class Transposition(object):
    # a transposition is a permutation of the set of symbols in a block
    def apply(self, block, key):
        return ''.join(block[index] for index in key)
        
    def reverse(self, block, key):
        result = bytearray(len(block))
        for index, symbol in zip(key, block):
            result[index] = symbol
        return bytes(result)

    def generate_key(self, block_size):
        key = [index for index in xrange(block_size)]
        random.shuffle(key)
        return key
        
        
def test_bijection():
    backwards = ''.join(reversed(ASCII))
    mapping = dict((key, backwards[index]) for index, key in enumerate(ASCII))
    bijection = Bijection([mapping])
    applied = bijection.apply(test_message)
    _test_message = bijection.reverse(applied)
    #print applied
    #print _test_message    
    assert test_message == _test_message

    
def test_monoalphabetic_substitution(): 
    permutation_key = Permutation.create_key(ASCII)
    permutation = Permutation([permutation_key])
    permuted = permutation.apply(test_message)
    original = permutation.reverse(permuted)
    print test_message
    print permuted
    print original
    assert test_message == original

    # test index wraparound
    test_message1 = chr(0) + " testagain\n" + chr(255)
    permuted1 = permutation.apply(test_message1)
    original1 = permutation.reverse(permuted1)
    assert test_message1 == original1
    
def test_polyalphabetic_substitution():
    keys = [Permutation.create_key(ASCII) for x in xrange(5)]
    permutation = Permutation(keys)
    permuted_again = permutation.apply(test_message)
    back_again = permutation.reverse(permuted_again)
    #print test_message
    #print permuted_again
    #print back_again
    assert back_again == test_message
    
def test_transposition():    
    transposition = Transposition()
    t_key = transposition.generate_key(len(test_message))    
    transposed = transposition.apply(test_message, t_key)
    transposed_back = transposition.reverse(transposed, t_key)
    #print test_message
    #print transposed
    #print transposed_back
    assert transposed_back == test_message
    
if __name__ == "__main__":
    test_message = "Hi. This is a test message that could use more distribution"
    test_bijection()
    
    test_monoalphabetic_substitution()
    test_polyalphabetic_substitution()
    test_transposition()