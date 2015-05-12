import pickle
import tokenize
import string
import sys
import pydoc
from StringIO import StringIO
from random import randint

import sys
from keyword import kwlist as keywords

DICTIONARY = dict((keyword, keyword) for keyword in keywords)
characters = ['\t', ":", ',', '.', "(", ")", "\n", "#", "=", "+", "-", "*", "&", "%", "!", '[', ']', '{', '}', '"', "'", "\\", '/', "'''", '"""', '<', '>']
for x in xrange(10):
    characters.append(chr(x))
for character in characters:
    DICTIONARY[character] = character
DICTIONARY[""] = ""

for module_name in sys.builtin_module_names:
    DICTIONARY[module_name] = module_name

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

You may redefine any keyword by reassigning it's value in this dictionary.
Some examples:

    dialect["def"] = "define a function", # a more verbose syntax
    dialect["yield"] = "return and continue", # an alternative syntax
    dialect["with"] = "@c#*(&DI9" # an obfuscated syntax
    dialect["import"] = "ICANHAZ" # an obnoxious syntax
"""
    
verbose_dialect = DICTIONARY.copy()
verbose_dialect["and"] = "and"
verbose_dialect["as"] = "referred to as"
verbose_dialect["assert"] = "Make sure that"
verbose_dialect["break"] = "Move on from this loop"
verbose_dialect["class"] = "What is a"
verbose_dialect["continue"] = "Handle the next iteration"
verbose_dialect["def"] = "How does it"
verbose_dialect["del"] = "Decrement the reference counter of"
verbose_dialect["elif"] = "If not and"
verbose_dialect["else"] = "If not then"
verbose_dialect["except"] = "So prepare for the exception(s)"
verbose_dialect["exec"] = "Execute"
verbose_dialect["finally"] = "Ensure this happens"
verbose_dialect["for"] = "For each"
verbose_dialect["from"] = "From the idea"
verbose_dialect["global"] = "Using the global value for"
verbose_dialect["if"] = "Supposing that"
verbose_dialect["import"] = "Import the idea of"
verbose_dialect["is"] = "Literally is"
verbose_dialect["lambda"] = "Short instruction"
verbose_dialect["not"] = "not"
verbose_dialect["or"] = "or"
verbose_dialect["pass"] = "Don't worry about it"
verbose_dialect["print"] = "Print to console"
verbose_dialect["raise"] = "Stop because there might be a problem"
verbose_dialect["return"] = "The result is"
verbose_dialect["try"] = "This might not work"
verbose_dialect["while"] = "While"
verbose_dialect["with"] = "In a new context, with"
verbose_dialect["yield"] = "Remember this context for later, lets work on"
#verbose_dialect["#"] = "Sidenote:" # does not work
verbose_dialect["="] = "="
verbose_dialect["!="] = "does not equal"
verbose_dialect[":"] = ":"
verbose_dialect[">="] = "is greater then or equal to"
verbose_dialect[">="] = "is less then or equal to"
verbose_dialect["=="] = "is equal to"

lol_dialect = DICTIONARY.copy()
lol_dialect["and"] = "and"
lol_dialect["as"] = "but to me its"
lol_dialect["assert"] = "Make sure that"
lol_dialect["break"] = "Shatter a vase LOL"
lol_dialect["class"] = "What is a"
lol_dialect["continue"] = "Handle the next iteration"
lol_dialect["def"] = "wat do"
lol_dialect["del"] = "Decrement the reference counter of"
lol_dialect["elif"] = "If not and"
lol_dialect["else"] = "If not then"
lol_dialect["except"] = "So prepare for the exception(s)"
lol_dialect["exec"] = "Execute"
lol_dialect["finally"] = "Ensure this happens"
lol_dialect["for"] = "For each"
lol_dialect["from"] = "Give me"
lol_dialect["global"] = "Using the global value for"
lol_dialect["if"] = "Supposing that"
lol_dialect["import"] = "ICANHAZ"
lol_dialect["is"] = "Literally is"
lol_dialect["lambda"] = "Short instruction"
lol_dialect["not"] = "not"
lol_dialect["or"] = "or"
lol_dialect["pass"] = "Don't worry about it"
lol_dialect["print"] = "Print to console"
lol_dialect["raise"] = "Stop because there might be a problem"
lol_dialect["return"] = "The result is"
lol_dialect["try"] = "This might not work"
lol_dialect["while"] = "While"
lol_dialect["with"] = "In a new context, with"
lol_dialect["yield"] = "Remember this context for later, lets work on"
#lol_dialect["#"] = "Sidenote:" # does not work
lol_dialect["="] = "="
lol_dialect["!="] = "does not equal"
lol_dialect[":"] = ":"
lol_dialect[">="] = "is greater then or equal to"
lol_dialect[">="] = "is less then or equal to"
lol_dialect["=="] = "is equal to"

class Dialect(object):
    """ usage: dialect = Dialect(dictionary) # create a dialect which switches keys for values
        modified_input = dialect.translate(input) # perform the translation on text string
        original_input = dialect.translate(modified_input, "from") # reverse a translation"""
        
    def __init__(self, **kwargs):
        self.dictionary = kwargs

    def from_object(self, object):
        source = inspect.getsource(object)
        return self.translate(StringIO(source))
        
    def translate_to_file(self, input_file, output_file):
        output_file.write(self.translate(input_file))
        
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
            

if __name__ == "__main__":
    import sys
    translator = Dialect(**verbose_dialect)
    filename = sys.modules["__main__"].__file__
    with open('network.py', 'r') as _file:
        source = _file.read()
        _file.seek(0)
        translated = translator.translate(_file)    
    print translated

