from cStringIO import StringIO

import base
import defaults
                        
class Stdin(base.Base):
    
    defaults = defaults.Stdin
    
    def __init__(self, **kwargs):
        self.available = False
        super(Stdin, self).__init__(**kwargs)
        self._readline_thread = self.readline_thread()
        self.file = StringIO()
        
    def read(self, size=None):
        file = self.file
        seek = file.seek        
        seek(0)
        all = file.read()
        seek(0)
        file.truncate()
        if size is None:
            size = len(all)
        file.write(all[size:])
        string = all[:size]
        return string
        
    def readline_thread(self):
        file = self.file
        seek = file.seek
        read = file.read
        write = file.write
        truncate = file.truncate
        string = ''
        while True:
            if self.available:
                seek(0)
                string = read()
                if "\n" in string:
                    index = string.index('\n') + 1
                    new = string[:index]
                    remaining = string[index:]
                    seek(0)
                    truncate()
                    write(remaining)
                else:
                    string = ''
            yield string
            
    def readline(self):
        """usage: stdin.readline() => string.
        
        Will return '' if no full line is available"""
        return next(self._readline_thread)
        
    def write(self, bytes):
        self.available = True
        self.file.write(bytes)