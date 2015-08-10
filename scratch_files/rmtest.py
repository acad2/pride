import collections

class Reversible_Mapping(object):
    
    def __init__(self, dictionary=None, max_size=None, **kwargs):
        self.keys = collections.deque(maxlen=max_size)
        self.values = collections.deque(maxlen=max_size)
        self.key_index_tracker = {}
        self.value_index_tracker = {}
        
        if dictionary:
            dictionary.update(kwargs)
            for key, value in dictionary.items():
                self[key] = value
        elif kwargs:        
            for key, value in kwargs.items():
                self[key] = value
            
    def __setitem__(self, key, value):
        try:
            index = self.key_index_tracker[key]
        except KeyError:
            pass
        else:
            self.keys.pop(index)
            self.values.pop(index)
            
        self.keys.append(key)
        self.values.append(value)
        self.value_index_tracker[id(value), value] = self.key_index_tracker[key] = len(self.keys) - 1
        
    def __getitem__(self, key):
        return self.values[self.key_index_tracker[key]]
        
    def reverse_lookup(self, value):
        return self.keys[self.value_index_tracker[id(value), value]]
        
if __name__ == "__main__":
    rm = Reversible_Mapping({"again" : 1, None: True})
    rm['test'] = 1
    rm[True] = 2
    
    print rm['test']
    print rm.reverse_lookup(2)
    
    print rm.reverse_lookup(1)
    