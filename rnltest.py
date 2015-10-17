import mpre

# relative instance name lookup. i.e. "Python.Network.Rpc_Server"
def relative_name_lookup(relative_name):
    instances = relative_name.split('.')
    _instance = mpre.objects[instances.pop(0)]
    numbers = ''.join(str(x) for x in xrange(10))
    while instances:
        instance_type = instances.pop(0)
        for amount, character in enumerate(reversed(instance_type)):
            if character not in numbers:
                break
        if amount:
            _instance_type = instance_type[:-amount] # slice numbers off the end
            instance_count = int(instance_type[-amount or -1:])
        else:
            _instance_type = instance_type
            instance_count = 0
        _instance = _instance.objects[_instance_type][instance_count]
    return _instance
       