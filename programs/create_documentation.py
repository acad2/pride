import pride.utilities
import pride.base

class Documentation_Creator(pride.base.Base):
        
    defaults = {"object_name" : '', "parse_args" : True}

    def __init__(self, **kwargs):
        super(Documentation_Creator, self).__init__(**kwargs)        
        self.create("pride.package.Documentation", resolve_string(self.object_name))
    
if __name__ == "__main__":  
    documentation_creator = Documentation_Creator()
    # and done!