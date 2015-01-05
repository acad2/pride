import pydoc
from StringIO import StringIO

class Module_Listing(object):
    
    def __init__(self, **kwargs):
        super(Module_Listing, self).__init__()
        [setattr(self, key, value) for key, value in kwargs.items()]
        setattr(self, "file", getattr(self, "file", StringIO()))
        
    def from_help(self):
        helper = pydoc.Helper(output=self.file)
        helper("modules")
        
    def read_file(self):
        file = self.file
        file.seek(0)
        text = file.read()
        return text    
        
    def trim(self, text):
        _file = StringIO(text)
        found = []
        count = 0
        for line in _file.readlines():
            if line.split(" ").count("") > 2:
                found += line.split()
                
        return ' '.join(found)
        
    def get_modules(self):
        self.from_help()
        original = self.read_file()
        return self.trim(original)
     
    def make_file(self, filename):
        with open(filename, 'w') as _file:
            _file.write(self.get_modules())
            _file.flush()
            _file.close()
        
        
