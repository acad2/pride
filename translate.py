def to_binary(string):
    return ' '.join(format(ord(character), 'b').zfill(8) for character in string)

def from_binary(bytes):
    return ''.join(chr(int(octet, 2)) for octet in bytes.split())