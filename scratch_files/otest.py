import keyword
import tokenize
import StringIO
import string
import random

LETTERS = string.letters

class Obfuscator(object):
    
    def new_name(self, value, current_values):
        new_value = ''
        while True:
            new_value = ''.join(random.choice(LETTERS) for 
                                x in xrange(0, random.randint(3, 9)))
            if new_value not in current_values:
                break
        current_values.add(new_value)
        return new_value
        
    def obfuscate_source(self, source_file, obfuscated_names=None):
        current_values = set()
        new_source = []
        obfuscated_names = obfuscated_names or {}
        for number, token_value, _, _, _ in tokenize.generate_tokens(source_file.readline):
            if number in (1, 3) and token_value not in keyword.kwlist:
                try:
                    token_value = obfuscated_names[token_value]
                except KeyError:                                    
                    new_name = self.new_name(token_value, current_values)
                    obfuscated_names[token_value] = new_name
                    token_value = obfuscated_names[token_value]
            new_source.append((number, token_value))            
        return tokenize.untokenize(new_source), obfuscated_names
                
    def deobfuscate_source(self, source, obfuscated_names):
        obfuscated_names = dict((value, key) for key, value in obfuscated_names.items())
        if isinstance(source, str):
            source = StringIO.StringIO(source)
        new_source = []
        for number, token_value, _, _, _ in tokenize.generate_tokens(source.readline):
            if number in (1, 3) and token_value not in keyword.kwlist:
        #        print "Swapping: ", token_value
                token_value = obfuscated_names[token_value]
            new_source.append((number, token_value))
        return tokenize.untokenize(new_source)
        
if __name__ == "__main__":
    obfuscator = Obfuscator()
    with open("base.py", 'r') as _file:
        osource, key = obfuscator.obfuscate_source(_file)
    #    print osource
     #   resource = obfuscator.deobfuscate_source(osource, key)
     #   compile(resource, 'test', 'exec')
        
    with open("network.py", 'r') as _file:
        osource, key = obfuscator.obfuscate_source(_file, key)
        print osource
        resource2 = obfuscator.deobfuscate_source(osource, key)
        compile(resource2, 'test', 'exec')