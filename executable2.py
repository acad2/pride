import os

import pride.base

class Exe(pride.base.Base):
    
    defaults = {"filename" : ''}
    required_attributes = ("filename", )
    parser_modifiers = {"filename" : {"types" : ("positional", )}}
    
    def __init__(self, **kwargs):
        super(Exe, self).__init__(**kwargs)
        filename = self.filename
        os.system("cython {} --embed".format(filename))
        
        filename = os.path.splitext(os.path.split(filename)[1])[0]
        os.system("gcc {}.c -IC:\Python27\include -LC:\Python27\libs\ -lpython27 -o {}.exe".format(filename, filename))

if __name__ == "__main__":
    Exe(parse_args=True)
        