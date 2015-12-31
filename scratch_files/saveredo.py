class Save(pride.base.Base):
    
    def __init__(self, **kwargs):
        super(Save, self).__init__(**kwargs)
        if not self.component:
            raise pride.base.ArgumentError("No component specified for saving")
            
        component = self.component
        try:
            attributes = component.__getstate__()
        except AttributeError:
            attributes = component.__dict__
            
        saved = {component.reference : attributes}
        
        for key, value in attributes["objects"].items():
            if hasattr(value, "reference"):
                try:
                    saved[value.reference] = value.__getstate__()
                except AttributeError:
                    saved[value.reference] = value.__dict__