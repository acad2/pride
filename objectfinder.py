import gc

def find_locations(_object):
    locations = []
    _globals = globals()
    globals_id = id(_globals)
    globals_items = _globals.items()
    print "\nFinding all references to: ", _object
    referrers = [id(item) for item in gc.get_referrers(_object)]
    if globals_id in referrers:
        for key, value in globals_items:
            if value == _object:
                print "Object is stored in globals as: ", key
                locations.append(("globals", key, None))
    
    for key, value in globals_items:
        value_id = id(value)
        if value_id in referrers:
            try:
                index = value.index(_object)
            except AttributeError:
                for _key, _value in value.items():
                    if _value == _object:
                        index = _key
            locations.append(("globals", key, index))
        else:
            try:
                search_iterable_for_memory_address(value, referrers, locations)
            except (TypeError, ValueError):
                continue
    return locations
    
def search_iterable_for_memory_address(_object, memory_addresses, locations):    
    try:
        for _key, _value in _object.items():
            if id(value) in memory_addresses:
                locations.append((_object, _key))
            else:
                try:
                    return search_iterable_for_memory_address(_value, memory_addresses, locations)
                except TypeError:
                    continue
    except AttributeError:   
        if not isinstance(_object, str) or isinstance(_object, unicode):
            for index, item in enumerate(_object):
                if id(item) in memory_addresses:
                    return (_object, index)
                else:
                    print "Searching: ", item
                    try:
                        return search_iterable_for_memory_address(item, memory_addresses, locations)
                    except TypeError:
                        continue
    raise ValueError("{} not found anywhere in {}".format(memory_addresses, _object))

if __name__ == "__main__":
    x = 10
    y = [x, 11, 12]
    z = [y, (1, 2, 3)]
    print find_locations(x)