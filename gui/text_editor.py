import pride.gui.gui
import pride.gui.widgetlibrary

class File_Button(pride.gui.widgetlibrary.Popup_Button):
    
    defaults = {"_popup_type" : "pride.gui.text_editor.File_Menu",
                "text" : "File", "pack_mode" : "left"}
            

class Edit_Button(pride.gui.gui.Button):
                
    defaults = pride.gui.gui.Button.defaults.copy()
    defaults.update({"text" : "Edit",
                     "pack_mode" : "left"})
    
 
class Options_Button(pride.gui.gui.Button):
    
    defaults = pride.gui.gui.Button.defaults.copy()
    defaults.update({"text" : "options",
                     "pack_mode" : "left"})
    
    
class File_Menu(pride.gui.gui.Container):
                
    defaults = pride.gui.gui.Container.defaults.copy()
    defaults.update({"startup_components" : ("pride.gui.text_editor.New_Button",
                                             "pride.gui.text_editor.Open_Button",
                                             "pride.gui.text_editor.Save_Button")})
                                             
    def __init__(self, **kwargs):
        super(File_Menu, self).__init__(**kwargs)
        self.create("pride.gui.widgetlibrary.Exit_Button", 
                    target=self.editor_instance)
                    
                    
class New_Button(pride.gui.gui.Button):
                 
    defaults = pride.gui.gui.Button.defaults.copy()
    defaults.update({"text_file_type" : "pride.gui.text_editor.Text_File"})
    
    def left_click(self, mouse):
        pride.objects[self.editor_instance].create(self.text_file_type)
        
        
class Open_Button(pride.gui.gui.Button):
            
    defaults = {"text_file_type" : "pride.gui.text_editor.Text_File"}
    
    def left_click(self, mouse):
        #self.create("pride.gui.widgetlibrary.Text
        pride.objects[self.editor_instance].create(self.text_file_type,
                                                  filename=filename)
        
 
class Save_Button(pride.gui.gui.Button):
    
    def left_click(self, mouse):
        pass
        
        
class Text_File(pride.gui.gui.Window):
            
    defaults = {"allow_text_edit" : True,
                "pack_mode" : "top"}
    
    def text_entry(self, text):
        print text
        super(Text_File, self).text_entry(text)
        
        
class Text_Editor(pride.gui.gui.Application):
    
    defaults = {"startup_components" : tuple()}
    
    def __init__(self, **kwargs):
        super(Text_Editor, self).__init__(**kwargs)
        self.create("pride.gui.widgetlibrary.Task_Bar", pack_mode="top",
                    startup_components=("pride.gui.text_editor.File_Button",
                                        "pride.gui.text_editor.Edit_Button",
                                        "pride.gui.text_editor.Options_Button"))
        self.create("pride.gui.gui.Window")
       # self.create("pride.gui.Container", 
        #            startup_components=("
        self.create("pride.gui.text_editor.Text_File")
        
        
class Shortcut(pride.gui.widgetlibrary.Icon):
            
    defaults = {"popup_type" : "pride.gui.text_editor.Text_Editor", "text" : "Text Editor"}
    