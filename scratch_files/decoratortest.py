import importlib
import inspect

import mpre._compile

def find_source_body(_object):
    """ Returns the body of the source code of the object. The body
        consists of all that follows the def/class statement and docstring. """
    source = inspect.getsource(_object)
    calling_function = in_slice = in_dictionary = 0
    in_string1 = in_string2 = in_string3 = in_string4 = 0
    for index, character in enumerate(source):
        if character == "{":
            in_dictionary += 1
        elif character == "}":
            in_dictionary -= 1
        elif character == "[":
            in_slice += 1
        elif character == "]":
            in_slice -= 1
        elif character == "'":
            if in_string1:
                in_string1 -= 1
            else:
                in_string1 += 1
        elif character == '"':
            if in_string2:
                in_string2 -= 1
            else:
                in_string2 += 1
        elif character == '"""':
            if in_string3:
                in_string3 -= 1
            else:
                in_string3 += 1
        elif character == "'''":
            if in_string4:
                in_string4 -= 1
            else:
                in_string4 += 1
        elif character == ':':
            if not (calling_function or in_slice or in_dictionary or
                    in_string1 or in_string2 or in_string3 or in_string4):
                index += 1 # start after the : that ends the def statement 
                break
    if '"""' in source:
        start_of_docstring = source.index('"""') + len('"""')
        end_of_docstring = source[start_of_docstring:].index('"""')
        index = end_of_docstring + start_of_docstring + len('"""')
    elif "'''" in source:
        start_of_docstring = source.index("'''") + len("'''")
        end_of_docstring = source[start_of_docstring:].index("'''")
        index = end_of_docstring + start_of_docstring + len("'''")
    return source, index
    
class Compiled(object):
        
    def __init__(self, **kwargs):
        self.types = kwargs
        
    def __call__(self, function):
        source, index = find_source_body(function)
        first_line = source.split('\n', 1)[0].replace("\t", "    ")
        indentation = 1
        indent = "    "
        spacing_size = len(indent)
        while first_line[:spacing_size] == indent:
            indentation += 1
            first_line = first_line[spacing_size:]
        spacing = indentation * indent
        type_declarations = ("{}cdef {} {}".format(spacing, _type, name) for
                             name, _type in self.types.items())
        start_of_def = source.index("def ")
        source = (source[start_of_def:index] + '\n' + 
                  '\n'.join(type_declarations) + source[index:])
        print source
        filename = "{}_compiled".format(function.__name__)
        with open(filename + ".py", 'wb') as _file:
            _file.write(source)
        mpre._compile.py_to_compiled([filename + ".py"], "pyd")
        pyd_module = importlib.import_module(filename)
        return getattr(pyd_module, function.__name__)
        
@Compiled(x="int")
def test_function(*args, **kwargs):
    x = 1
        
if __name__ == "__main__":
    #print get_source_body(get_source_body)
    test_function()