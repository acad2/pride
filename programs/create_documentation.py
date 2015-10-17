import pride.utilities
import pride.base

class Documentation_Creator(pride.base.Base):
    
    defaults = pride.base.Base.defaults.copy()
    defaults.update({"object_name" : '',
                     "parse_args" : True})

    def __init__(self, **kwargs):
        super(Documentation_Creator, self).__init__(**kwargs)
        print self, self.object_name
        self.create("pride.package.Documentation", 
                    pride.utilities.resolve_string(self.object_name))
    
if __name__ == "__main__":  
    documentation_creator = Documentation_Creator()
    # and done!