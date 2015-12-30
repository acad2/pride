import heapq

import pride.base

class Index_Preserving_List(pride.base.Wrapper):
    """ A list that preserves the index of each item when an item is added or removed. """
    blank_space = []
    
    mutable_defaults = {"_storage" : list, "blank_spaces" : list,
                        "wrapped_object" : list}
    
    wrapped_object_name = "list"
        
    def append(self, item):
        storage = self.list
        try:
            index = heapq.heappop(self.blank_spaces)
        except IndexError:
            storage.append(item)
        else:
            storage.insert(index, item)
            del storage[index + 1]
        
    def remove(self, item):
        storage = self.list
        index = storage.index(item)
        heapq.heappush(self.blank_spaces, index, )        
        storage.insert(index, self.blank_space)
        del storage[index + 1]
    
    def __str__(self):
        return str(self.list)        
    
    @staticmethod
    def unit_test():
        l = Index_Preserving_List()
        for x in xrange(5):
            l.append(x)
        l.remove(3)
        l.append(27)
        
        l.remove(0)
        l.append("testing!")
        assert l.list == ["testing!", 1, 2, 27, 4]
    
if __name__ == "__main__":
    Index_Preserving_List.unit_test()