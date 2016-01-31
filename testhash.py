from hashlib import sha256
def test():
    strings = ['string1', 'string2', '\x00', '\\x00']
    tohash = ''.join(str(position) + string for position, string in enumerate(strings))
    result = sha256(tohash).hexdigest()
    print result
    
test()    