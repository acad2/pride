import pride.gui.gui
import pride.gui.widgetlibrary

class Iterable(pride.gui.gui.Container):
        
    def __init__(self, _list, **kwargs):
        super(Iterable, self).__init__(**kwargs)
        self.create("pride.gui.widgetlibrary.Task_Bar")
        for item in _list:
            self.create(Object_Button, item, pack_mode=self.pack_mode)
            
            
class Dictionary(pride.gui.gui.Container):
                
    def __init__(self, _dict, **kwargs):
        super(Dictionary, self).__init__(**kwargs)
        self.create("pride.gui.widgetlibrary.Task_Bar")
        left = self.create("pride.gui.gui.Container", pack_mode="left")
        right = self.create("pride.gui.gui.Container", pack_mode="right")
        for key, value in _dict.items():
            left.create("pride.gui.gui.Button", text=key)
            right.create(Object_Button, value)
            
            
class Object_Button(pride.gui.widgetlibrary.Popup_Button):
                
    defaults = {"popup_type" : Dictionary, "opener" : None}
    
    def __init__(self, _object, **kwargs):
        super(Object_Button, self).__init__(**kwargs)
        self.text = repr(_object) if hasattr(_object, "reference") else str(_object)
        self._object = _object
    
    def left_click(self, mouse):
        if self._popup:
            self._popup.delete()
        elif self.popup_type:
            self.alert("Creating: {}".format(self.popup_type), level='vv')
            if self.opener:
                creator = pride.objects[self.opener]
            else:
                creator = self
            self._popup = creator.create(self.popup_type, self._object.__dict__)        
            