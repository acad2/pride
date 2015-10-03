import mpre.gui.gui
import mpre.gui.widgetlibrary

class File_Button(mpre.gui.gui.Button):
    
    defaults = mpre.gui.gui.Button.defaults.copy()
    defaults.update({"_file_menu" : '',
                     "text" : "File",
                     "pack_mode" : "horizontal"})
    
    def left_click(self, mouse):
        if not self._file_menu:
            self._file_menu = self.create(File_Menu)
        else:
            self._file_menu.delete()
            

class Edit_Button(mpre.gui.gui.Button):
                
    defaults = mpre.gui.gui.Button.defaults.copy()
    defaults.update({"text" : "Edit",
                     "pack_mode" : "horizontal"})
    
 
class Options_Button(mpre.gui.gui.Button):
    
    defaults = mpre.gui.gui.Button.defaults.copy()
    defaults.update({"text" : "options",
                     "pack_mode" : "horizontal"})
    
    
class File_Menu(mpre.gui.gui.Container):
                
    defaults = mpre.gui.gui.Container.defaults.copy()
    defaults.update({"startup_components" : ("mpre.gui.text_editor.New_Button",
                                             "mpre.gui.text_editor.Open_Button",
                                             "mpre.gui.text_editor.Save_Button")})
                                             
    def __init__(self, **kwargs):
        super(File_Menu, self).__init__(**kwargs)
        self.create("mpre.gui.widgetlibrary.Exit_Button", 
                    target=self.editor_instance)
                    
                    
class New_Button(mpre.gui.gui.Button):
                 
    defaults = mpre.gui.gui.Button.defaults.copy()
    defaults.update({"text_file_type" : "mpre.gui.text_editor.Text_File"})
    
    def left_click(self, mouse):
        mpre.objects[self.editor_instance].create(self.text_file_type)
        
        
class Open_Button(mpre.gui.gui.Button):
            
    defaults = mpre.gui.gui.Button.defaults.copy()
    defaults.update({"text_file_type" : "mpre.gui.text_editor.Text_File"})
    
    def left_click(self, mouse):
        #self.create("mpre.gui.widgetlibrary.Text
        mpre.objects[self.editor_instance].create(self.text_file_type,
                                                  filename=filename)
        
 
class Save_Button(mpre.gui.gui.Button):
    
    def left_click(self, mouse):
        pass
        
        
class Text_File(mpre.gui.gui.Window):
            
    defaults = mpre.gui.gui.Window.defaults.copy()
    defaults.update({"allow_text_edit" : True,
                     "pack_mode" : "vertical"})
    
    
class Text_Editor(mpre.gui.widgetlibrary.Application):
    
    defaults = mpre.gui.widgetlibrary.Application.defaults.copy()
    defaults.update({"startup_components" : tuple()})
    
    def __init__(self, **kwargs):
        super(Text_Editor, self).__init__(**kwargs)
        self.create("mpre.gui.widgetlibrary.Task_Bar", pack_mode="top",
                    startup_components=("mpre.gui.text_editor.File_Button",
                                        "mpre.gui.text_editor.Edit_Button",
                                        "mpre.gui.text_editor.Options_Button"))
       # self.create("mpre.gui.Container", 
        #            startup_components=("
        self.create("mpre.gui.text_editor.Text_File", )