""" Module for datastructures of various kinds. Objects defined here may not 
    be employed elsewhere in pride; they're just potentially generally useful 
    and not already defined in the standard library (to my knowledge) 
    
    Objects defined here should not rely on pride for anything - regular python only. """    
import collections
import heapq
import timeit

timer_function = timeit.default_timer 

class Latency(object):
    """ usage: Latency([name="component_name"], 
                       [size=20]) => latency_object
                       
        Latency objects possess a start_measuring and )"""
     
    def _get_last_measurement(self):
        try:
            return self._average.values[-1]
        except IndexError:
            return timer_function() - self.started_at
    last_measurement = property(_get_last_measurement, doc="Gets the last measurement")
    
    def _get_average_measurement(self):
        return self._average.average
    average = property(_get_average_measurement)
    
    def _get_max_measurement(self):
        return max(self._average.values)
    maximum = property(_get_max_measurement)
    
    def _get_min_measurement(self):
        return min(self._average.values)
    minimum = property(_get_min_measurement)
    
    def _get_measurements(self):
        _average = self._average
        _values = _average.values
        return (min(_values), _average.average, max(_values))
    measurements = property(_get_measurements)
    
    def __init__(self, name='', size=20):
        super(Latency, self).__init__()
        self.name = name
        self._average = Average(size=size)
        self.started_at = timer_function()
        
    def mark(self):
        now = timer_function()
        self._average.add(now - self.started_at)        
        self.started_at = now
        
    def __str__(self):
        return "{} Latency".format(self.name, self.average)
        
        
class Average(object):
    """ usage: Average([name=''], [size=20], 
                       [values=tuple()], [meta_average=False]) => average_object
                       
        Average objects keep a running average via the add method.
        The size option specifies the maximum number of samples. When
        this limit is reached, additional samples will result in the
        oldest sample being removed.
        
        values may be used to seed the average.
        
        The meta_average boolean flag is used to determine whether or not
        to keep an average of the average - This is implemented by an
        additional Average object."""
        
    def _get_meta_average(self):
        average = self._meta_average.average
        if not average:
            average = self.average
        return average
    meta_average = property(_get_meta_average)

    def _get_range(self):
        values = self.values
        return (min(values), self.average, max(values))
    range = property(_get_range)
        
    def __init__(self, size=20, values=tuple(), meta_average=True):
        value = meta_average
        if meta_average:
            value = Average(30, meta_average=False)
        self._meta_average = value
        
        size = len(values) if values else size
        self.values = collections.deque(values, size)
        self.max_size = size
        self.size = float(len(self.values))
        if self.size:
            self.average = sum(self.values) / self.size
        else:
            self.average = 0
        self.add = self.partial_add

    def partial_add(self, value):
        self.size += 1
        self.values.append(value)
        self.average = sum(self.values) / self.size
        if self.size == self.max_size:
            self.add = self.full_add

    def full_add(self, value):
        old_value = self.values[0]
        adjustment = (value - old_value) / self.size
        self.values.append(value)
        self.average += adjustment
        if self._meta_average:
            self._meta_average.add(self.average)

                   
class LRU_Cache(object):
    """A dictionary with a max size that keeps track of
       key usage and handles key eviction. 
       
       currently completely untested"""
    def __init__(self, size=50, seed=None):
        if seed:
            assert len(seed.keys()) <= size
        else:
            seed = dict()
        seed = seed if seed else dict()
        keys = seed.keys()
        assert len(keys) <= size
        
        deque = self.deque = collections.deque(maxlen=size)
        deque.extend(keys)
        
        # testing x in ... is significantly faster with a set
        self.contains = set(keys)
        self.size = size
        
        # change implementations once cache is full
        self.add = self._add
        
        # when no entry has been evicted (cache is not full or entry was
        # already in it), return a non hashable object so all keys 
        # (None, False, etc) will remain usable.
        self.no_eviction = []
        
    def _add(self, item):
        deque = self.deque
        
        if item in self.contains:
            deque.remove(item)
        else:
            self.contains.add(item)
            
        deque.append(item)
        if len(deque) > self.size:
            # change to a slightly different implementation that
            # doesn't do this check when the cache becomes full
            self.add = self._full_add
        
        return self.no_eviction
        
    def _full_add(self, item):
        deque = self.deque
        contains = self.contains
        
        if item in contains:
            deque.remove(item)
            evicted = self.no_eviction
        else:
            contains.add(item)
            evicted = deque[0]
        deque.append(item)
        return evicted
              
    def __getitem__(self, key):
        evicted = self.tracker.add(key)
        dict = self.dict
        if evicted is not self.no_eviction:
            del dict[evicted]
            self.contains.remove(evicted)
        return dict[key]
        
    def __setitem__(self, key, value):
        self.dict[key] = value
        self.contains.add(key)    
        
        
class Reversible_Mapping(object):
    
    def __init__(self, dictionary=None, **kwargs):
        self.keys, self.values = [], []
        self.key_index_tracker, self.value_index_tracker = {}, {}
                
        if dictionary:
            dictionary.update(kwargs)
            for key, value in dictionary.items():
                self[key] = value
        elif kwargs:        
            for key, value in kwargs.items():
                self[key] = value
    
    def items(self):
        return [(key, self.values[index]) for index, key in
                enumerate(self.keys)]
                
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
        self.value_index_tracker[value] = self.key_index_tracker[key] = len(self.keys) - 1
        
    def __getitem__(self, key):
        return self.values[self.key_index_tracker[key]]
        
    def reverse_lookup(self, value):
        return self.keys[self.value_index_tracker[value]]    
        
    def __contains__(self, key):
        return key in self.key_index_tracker
        
    def __str__(self):
        return str(dict((zip(self.keys, self.values))))
             
    
class Index_Preserving_List(object):
    """ A list that preserves the index of each item when an item is added or removed. """
    blank_space = []             
    
    dont_wrap = ("append", "remove", "__class__", "__dict__",
                 "__delattr__", "__delitem__", "__delslice__",
                 "__doc__", "__getattribute__", "__getitem__",
                 "__getslice__", "__init__", "__new__",
                 "__reduce__", "__reduce_ex__", "__repr__",
                 "__setattr__", "__setitem__", "__setslice__",
                 "__subclasshook__")
    def __init__(self, _list=None):
        _list = _list or []
        self.blank_spaces = []
        dont_wrap = self.dont_wrap
        for attribute_name in dir(_list):
            if attribute_name not in dont_wrap:
                #print "Setting attribute: ", attribute_name
                setattr(self, attribute_name, getattr(_list, attribute_name))
        self.list = _list
                
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
    
    def __contains__(self, item):
        return item in self.list
    
    def __iter__(self):
        return iter(self.list)
    
  #  def __next__(self):
        
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