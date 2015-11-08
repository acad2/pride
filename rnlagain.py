def split_instance_name(instance_name):
    for index, character in enumerate(reversed(instance_name)):
        try:
            number = int(character)
        except ValueError:
            break
    try:
        number = int(instance_name[-index:])
    except ValueError:
        number = 0
    return (instance_name[:index], number)
    
def xor(input_one, input_two):
    return (input_one or input_two) and not (input_one and input_two)
    
def dereference(instance_names='', _object=None, packed_args=tuple(),
                delimiter='->'):
    if not xor(instance_names, packed_args):
        raise ValueError("Received instance_names and packed_args arguments; expected either, not both")
    if instance_names:
        packed_args = tuple(split_instance_name(name) for name in instance_names.split(delimiter))    
    start_index = 0
    if not _object:
        instance_type, index = packed_args[0]
        _object = pride.environment.objects[instance_type][index]
        start_index = 1
    for instance_type, index in packed_args[start_index:]:
        try:
            _object = _object.objects[instance_type][index]
        except (KeyError, IndexError):
            raise ValueError("Unable to resolve {}".format(instance_names or packed_args))
    return _object
    
#if __name__ == "__main__":
    