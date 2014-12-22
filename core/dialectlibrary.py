import pickle
import tokenize
import string
import sys
from random import randint
from keyword import kwlist as keywords

"""
    dialect = dict((keyword, keyword) for keyword in keywords)

The above programmatically populates a dictionary using CPythons keywords. The
following dictionary would be equivalent:

    dialect = {"and" : "and",
               "as" : "as",
               "assert" : "assert",
               "break" : "break",
               "class" : "class",
               ... and so on

You may redefine any keyword by reassigning it's value in this dictionary
Some examples:

    dialect["def"] = "define a function", # a more verbose syntax
    dialect["yield"] = "return and continue", # an alternative syntax
    dialect["with"] = "@c#*(&DI9" # an obfuscated syntax

Any word in the dictionary can either be modified manually or automatically.
If done automatically, the default mode will not transpose any token names. This can
be changed to produce a random unique per name token name.
"""

DICTIONARY = dict((keyword, keyword) for keyword in keywords)
characters = ['\t', ":", ',', '.', "(", ")", "\n", "#", "=", "+", "-", "*", "&", "%", "!", '[', ']', '{', '}', '"', "'", "\\", '/', "'''", '"""', '<', '>']
for x in xrange(10):
    characters.append(chr(x))
for character in characters:
    DICTIONARY[character] = character
DICTIONARY[""] = ""

for module_name in sys.builtin_module_names:
    DICTIONARY[module_name] = module_name
    
class Dialect(object):

    def __init__(self, **kwargs):
        self.dictionary = kwargs

    def translate(self, _file):
        tokens = []
        token_generator = tokenize.generate_tokens(_file.readline)
        dictionary = self.dictionary

        for token_type, token_name, starts_at, ends_at, full_line in token_generator:
            if token_name in dictionary:
                token_name = dictionary[token_name]
            tokens.append((token_type, token_name, starts_at, ends_at, full_line))
        return tokenize.untokenize(tokens)

    def translate_from(self, _file):
        reverse_dictionary = dict((value, key) for key, value in self.dictionary.items())
        source = _file.read()
        for alternative, keyword in reverse_dictionary.items():
            source = source.replace(alternative, keyword)
        return source

    def save(self, filename, mode="self"):
        if mode == "dictionary":
            target = self.dictionary
        else:
            target = self
        with open(filename, "wb") as _file:
            _file.write(pickle.dumps(target))
            _file.flush()
            _file.close()


class Random_Dialect(Dialect):

    def __init__(self, **kwargs):  
        super(Random_Dialect, self).__init__(**kwargs)
        self.delimiters = ['\t', ":", ',', '.', "(", ")", "\n", "#", "=", "+", "-", "*", "&", "%", "!", '[', ']', '{', '}', '"', "'", "\\", '/', "'''", '"""', '<', '>']#characters#(".", ",", "(", ")", ":", "\n", '#', "'''", '"""')

    def random_word(self):
        letters = string.ascii_letters
        word = ''.join(letters[randint(0, len(letters)-1)] for x in xrange(1, randint(2, 8)))
        """limit = randint(33, 128)
        size = randint(2, 10)
        word = ''.join(chr(randint(33, limit)) for x in xrange(randint(2, size)))"""
        used = self.dictionary.values()
        while word in used:
            word = self.random_word()
        return word

    def translate(self, _file, mode="to"):
        _file_text = _file.read()     
        dictionary = self.dictionary   
        delimiters = self.delimiters
        _file_text = _file_text.replace("     ", '\t')
        if mode == "to":            
            for delimiter in delimiters:
                _file_text = _file_text.replace(delimiter, " {0} ".format(delimiter))          
        
        elif mode == "from":
            dictionary = dict((value, key) for key, value in dictionary.items())               

        __file = StringIO(_file_text)
        result = self._translate_file(__file, dictionary)
        if mode == "from":
            for delimiter in delimiters:
                result = result.replace(" {0} ".format(delimiter), delimiter)
        result = result.replace("\t", '     ')
        return result
        
    def _translate_file(self, _file, dictionary):
        new_file = []
        for line in _file.readlines():
            new_line = []
            for word in line.split(" "):
                new_token = self._translate_word(word, dictionary)              
                new_line.append(new_token)
            #    print "adding new token {0} from word {1}".format(new_token, word)
            #print "appending \n{0}\n{1}\n".format(new_line, " ".join(new_line))
            new_file.append(" ".join(new_line))
        return "".join(new_file)

    def _translate_word(self, word, dictionary):
        try:
            new_token = dictionary[word]
        except KeyError:
            try:
                new_token = dictionary[word] = str(int(word))
            except ValueError:
                end = ""
                if word and "\n" == word[-1]:
                    end = "\n"
                new_token = dictionary[word] = self.random_word() + end            
        return new_token

   
class Obfuscated_Dialect(Random_Dialect):
    
    def __init__(self, **kwargs):
        super(Obfuscated_Dialect, self).__init__(**kwargs)
        
    def obfuscate(self, _file, mode="to"):
        source = super(Obfuscated_Dialect, self).translate(_file, mode)
        for delimiter in self.delimiters:
            source = source.replace(" {0} ".format(delimiter), delimiter)
      #  source = source.replace("\t", '     ')
        return source
        
        
if __name__ == "__main__":
    import difflib
    from verbosedialect import verbose_dialect
    from cdialect import c_dialect
    from StringIO import StringIO
    difference = difflib.Differ()
    filename = "./networklibrary.py"
    _file = open(filename)
    source = _file.read()
    _file.seek(0)

    #print source
    """translated = verbose_dialect.translate(_file)
    print translated

    translated_file = StringIO(translated)
    translated_back = verbose_dialect.translate_from(translated_file)"""

    """translated = c_dialect.translate(_file)
    translated_flo = StringIO(translated)
    translated_back = c_dialect.translate_from(translated_flo)
    print translated"""

    key = Random_Dialect(**DICTIONARY)
    key.save("key.mpy", mode="dictionary")
    
    encrypted = key.translate(_file) 
    encrypted_file = open("{0}.mpy".format(filename), "w+")
    encrypted_file.write(encrypted)
    encrypted_file.flush()
    encrypted_file.seek(0)    
    _file.seek(0)
    #print encrypted[:2048]
    plain_text = key.translate(encrypted_file, "from")
    #print plain_text
    
    key2 = Obfuscated_Dialect(**DICTIONARY)
    obfuscated = key2.obfuscate(_file)
    obfuscated_file = open("{0}.opy".format(filename), "w+")
    obfuscated_file.write(obfuscated)
    obfuscated_file.flush()
    obfuscated_file.close()
    print obfuscated
    code = compile(obfuscated, 'encrypted', 'exec')
    exec code in locals(), globals()
    #try:
    assert plain_text == source
    #except AssertionError:
     #   print "Assertion Error"
      #  diff = difference.compare(source.splitlines(), plain_text.splitlines())
       # print "\n".join(diff)   
    #compile(encrypted, 'obfuscated', 'exec')
    code = compile(plain_text, "encrypted", "exec")
    exec code in locals(), globals()