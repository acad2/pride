import mpre.utilities
import mpre.base

class Documentation_Creator(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"object_name" : '',
                     "parse_args" : True})

    def __init__(self, **kwargs):
        super(Documentation_Creator, self).__init__(**kwargs)
        print self, self.object_name
        self.create("mpre.package.Documentation", 
                    mpre.utilities.resolve_string(self.object_name))
    
if __name__ == "__main__":  
    documentation_creator = Documentation_Creator()
    # and done!