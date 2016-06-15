import pride.gui.gui
       
        
class Python_Datatype_Button(pride.gui.gui.Button):

    def __init__(self, value, **kwargs):
        super(Python_Datatype_Button, self).__init__(**kwargs)
        self.value = value
        self.text = str(value)

        
class int_Button(Python_Datatype_Button): pass
    
   
class str_Button(Python_Datatype_Button): pass

        
class List(pride.gui.gui.Container):
    
    mutable_defaults = {"list" : list}
    
    def append(self, value):
        self.list.append(value)
        self.create("pride.gui.datatypes.{}_Button".format(value.__class__.__name__), value)
        
    def pop(self, index=-1):
        self.list.pop(index)
        self.stored_objects[index].delete()