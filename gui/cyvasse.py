import pride.gui.gui
import pride.gui.widgetlibrary            
    
class New_Button(pride.gui.gui.Button):
    
    defaults = {"text" : "New"}
    
    def left_click(self, mouse): 
        self.parent_application.create("pride.gui.cyvasse.Cyvasse_Gameboard")
        self.parent.delete()
        
        
class Open_Button(pride.gui.gui.Button):
    
    defaults = pride.gui.gui.Button.defaults.copy()
    defaults.update({"text" : "Open..."})
    
    def left_click(self, mouse):
        self.parent_application.create("pride.gui.widgetlibrary.File_Explorer",
                                       callback=self._open)
        self.parent.delete()
        
    def _open(self, filename):
        with open(filename, 'rb') as _file:
            saved_game = pride.base.load(_file=_file)
        self.parent_application.add(saved_game)
        
        
class Save_Button(pride.gui.widgetlibrary.Method_Button):
        
    defaults = {"text" : "Save",
                "method" : "save"}
                     
    def left_click(self, mouse):
        if not self.parent_application._current_save_file:
            self.create("pride.gui.widgetlibrary.File_Explorer", 
                        callback=self._open)
        else:
            super(Save_Button, self).left_click(mouse)
        self.parent.delete()
        
    def _open(self, filename):
        with open(filename, 'r') as _file:
            self.parent_application._current_save_file = self.instance_name
        super(Save_Button, self).left_click(None)
            
        
class Save_As_Button(pride.gui.widgetlibrary.Method_Button):
            
    defaults = {"text" : "Save As...",
                "method" : "save"}
    
    def left_click(self, mouse):
        self.create("pride.gui.widgetlibrary.File_Explorer", 
                    callback=self._open)
        self.parent.delete()
        
    def _open(self, filename):
        with open(filename, 'r') as _file:
            self.parent_application._current_save_file = self.instance_name
        super(Save_As_Button, self).left_click(None)    
        
        
class Close_Button(pride.gui.gui.Button):
            
    defaults = {"text" : "close"}
    
    def left_click(self, mouse):
        current_game = self.parent_application.current_game
        if current_game:
            current_game.delete()
        self.parent.delete()
        
        
class File_Menu(pride.gui.gui.Container):
    
    defaults = {"startup_components" : (New_Button, Open_Button,
                                        Close_Button),
                "pack_mode" : "drop_down_menu"}
    
    def __init__(self, **kwargs):
        super(File_Menu, self).__init__(**kwargs)
        self.create(Save_Button, target=self._get_current_game)
        self.create(Save_As_Button, target=self._get_current_game)
        
    def _get_current_game(self):
        return self.parent_application.current_game
        
    def delete(self):
        self.parent._file_menu = None
        super(File_Menu, self).delete()
        
        
class File_Button(pride.gui.gui.Button):
    
    defaults = {"text" : "File", "pack_mode" : "horizontal", 
                "_file_menu" : None}
    
    verbosity = {"file_menu_create" : 'vv', "file_menu_delete" : 'vv'}
    
    def left_click(self, mouse):
        if not self._file_menu:
            self.alert("Creating new file menu",
                       level = self.verbosity["file_menu_create"])
            self._file_menu = self.create(File_Menu)
            self._file_menu.pack()
        else:
            self._file_menu.delete()
            self._file_menu = None
            
            
class Cyvasse_Gameboard(pride.gui.gui.Window):
    
    defaults = pride.gui.gui.Window.defaults.copy()
    
    
class Cyvasse(pride.gui.gui.Application):
    
    defaults = {"startup_components" : tuple()}
    
    def _get_current_game(self):
        return (self._current_game or
                self.objects["Cyvasse_Gameboard"][0].instance_name if
                self.objects["Cyvasse_Gameboard"] else None)
    def _set_current_game(self, value):
        self._current_game = value
    current_game = property(_get_current_game, _set_current_game)
    
    def __init__(self, **kwargs):
        self._current_save_file = self._current_game = None
        super(Cyvasse, self).__init__(**kwargs)
        self.objects.setdefault("Cyvasse_Gameboard", [])
        self.create("pride.gui.widgetlibrary.Task_Bar", startup_components=(
                    File_Button, ))
        