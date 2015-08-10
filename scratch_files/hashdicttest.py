import mpre.misc.decoratorlibrary
Timed = mpre.misc.decoratorlibrary.Timed

def unpack_dict(dictionary):
    new = []
    for item in dictionary.keys() + dictionary.values():
        result = item
        if isinstance(item, list):
            result = tuple(item)
        elif isinstance(item, dict):
            result = unpack_dict(item)
        new.append(result)
    return tuple(new)
    
def hash_dict(dictionary):
    unpacked = str(dictionary)
    return hash(unpacked)
    
def hash_dict_test():
    di = {"testing" : True,
          10 : [1, 2, 3],
          1.0 : {'subtest' : 'whynot'}}
    
    for x in xrange(10000):
        hash_dict(di)
        
if __name__ == "__main__":
    time, results = Timed(hash_dict_test)()
    print "hashed 10000 dictionaries in: ", time