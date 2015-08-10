class Reference(object):
    
    references = {}
    
    def __new__(cls, base_object):
        name = base_object.instance_name
        references = cls.references
        if name not in references:
            self = super(Reference, cls).__new__(cls)
            self.id = name
            references[name] = self
        else:
            self = references[name]
        return self
    
    def __getattr__(self, attribute):
        return getattr(objects[self.id], attribute)

    def dereference(self):
        return objects[self.id]