import StringIO

def indent_lines(string, amount=1, spacing="    "):
    one = '\n'.join(spacing + line for line in string.split('\n'))
    file_like_object = StringIO.StringIO(string)
    two = ''.join(spacing + line for line in file_like_object.readlines()) 
    if not one == two:
        print ''.join(char for index, char in enumerate(one) if
                               two[index] != char)
    return one
    
with open("base.py", 'r') as _file:
    source = _file.read()
    indent_lines(source)