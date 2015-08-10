class Save(mpre.base.Base):
    
    def __init__(self, **kwargs):
        super(Save, self).__init__(**kwargs)
        if not self.component:
            raise mpre.base.ArgumentError("No component specified for saving")
            
        component = self.component
        try:
            attributes = component.__getstate__()
        except AttributeError:
            attributes = component.__dict__
            
        saved = {component.instance_name : attributes}
        
        for key, value in attributes["objects"].items():
            if hasattr(value, "instance_name"):
                try:
                    saved[value.instance_name] = value.__getstate__()
                except AttributeError:
                    saved[value.instance_name] = value.__dict__