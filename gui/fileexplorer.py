import time
import collections
import os

import pride.gui.widgetlibrary
import pride.gui.gui

class File_Explorer(pride.gui.gui.Application):
    
    defaults = {"current_working_directory" : '.', "filetype_filter" : ''}
                                     
    def __init__(self, **kwargs):
        self.file_details = collections.defaultdict(lambda: [])        
        super(File_Explorer, self).__init__(**kwargs)         
        
        current_directory = self.current_working_directory
        epoch_to_english = lambda _time: time.asctime(time.localtime(_time))
        for filename in os.listdir(current_directory):
            full_name = os.path.join(current_directory, filename)
            file_type = os.path.splitext(filename)[-1] or filename
            if ((file_type == self.filetype_filter and self.filetype_filter) or
                os.path.isfile(full_name)):
                self.file_details["Name"].append(filename)
                self.file_details["Type"].append(file_type)
                self.file_details["Size"].append(os.path.getsize(full_name))
                
                file_information = os.stat(full_name)
                
                self.file_details["Date_Created"].append(epoch_to_english(file_information.st_ctime))
                self.file_details["Date_Modified"].append(epoch_to_english(file_information.st_mtime))
        window = pride.objects[self.window]        
        window.create(Navigation_Bar)
        window.create(Directory_Viewer)                
        self.create(Info_Bar, pack_mode="bottom")
        self.create(File_Open_Prompt, background_color=(255, 255, 255, 0), pack_mode="bottom")
        

class Navigation_Bar(pride.gui.gui.Container):
            
    defaults = {"pack_mode" : "top", "h_range" : (0, 20)}
    
    def __init__(self, **kwargs):
        super(Navigation_Bar, self).__init__(**kwargs)
        self.create(Back_Button)
        self.create(Forward_Button)
        self.create(History_Dropdown)
        self.create(Ascend_Button)
        self.create(Search_Bar, 
                    callback=(self.parent_application.reference + "->Directory_Viewer",
                              "handle_input"))
        
   
class Back_Button(pride.gui.widgetlibrary.Method_Button):
    
    defaults = {"text" : "<-", "method" : "back", "pack_mode" : "left",}
       
    
class Forward_Button(pride.gui.widgetlibrary.Method_Button):
        
    defaults = {"text" : "->", "method" : "forward", "pack_mode" : "left"}
       

class History_Dropdown(pride.gui.widgetlibrary.Popup_Button):
        
    defaults = {"popup_type" : "pride.gui.fileexplorer.Directory_History",
                "pack_mode" : "left", "text" : "history"}
    flags = {"scale_to_text" : True}
    

class Ascend_Button(pride.gui.widgetlibrary.Method_Button):
            
    defaults = {"method" : "ascend_directory", "text" : "..", "pack_mode" : "left"}    
      
    
class Search_Bar(pride.gui.widgetlibrary.Prompt): 

    defaults = {"pack_mode" : "left", "scroll_bar_enabled" : True}        
    
        
class Places_Bar(pride.gui.gui.Container):
            
    defaults = {"pack_mode" : "left", "w_range" : (0, 200)}
    
    def __init__(self, **kwargs):
        super(Places_Bar, self).__init__(**kwargs)
        #self.create(Lru_Directory_Dropdown)
        #self.create(Remote_Host_Dropdown)
        

class Info_Bar(pride.gui.gui.Container):
            
    defaults = {"pack_mode" : "bottom", "h_range" : (0, 20)}
    
    def __init__(self, **kwargs):
        super(Info_Bar, self).__init__(**kwargs)
        #self.create(Item_Count_Indicator
        #self.create(Selection_Count_Indicator)
        #self.create(File_Size_Indicator)
        
        
class Directory_Viewer(pride.gui.gui.Window):
        
    defaults = {"pack_mode" : "main"}
    
    def __init__(self, **kwargs):
        super(Directory_Viewer, self).__init__(**kwargs)
        self.create(Places_Bar)
        viewer = self.create(Column_Viewer)
        self.create("pride.gui.widgetlibrary.Scroll_Bar", pack_mode="right",
                    target=(viewer.reference, "texture_window_y"))
                
    
class Column_Viewer(pride.gui.gui.Window):
        
    defaults = {"default_columns" : ("Type", "Name", "Size", 
                                     "Date_Created", "Date_Modified"),
                "pack_mode" : "left", "sorted_by" : "Type"}
                
    def __init__(self, **kwargs):
        super(Column_Viewer, self).__init__(**kwargs)
        for column_name in self.default_columns:
            container = self.create("pride.gui.gui.Container", pack_mode="left", scroll_bars_enabled=False)
            container.create(Sort_Button, text=column_name, h_range=(20, 20))
            if column_name == "Name":
                button_type = Filename_Button
            else:
                button_type = "pride.gui.widgetlibrary.Text_Box"
                    
            for file_detail in self.parent_application.file_details[column_name]:
                container.create(button_type, text=str(file_detail), pack_mode="top",
                                 h_range=(20, 20))
            
        
class Sort_Button(pride.gui.gui.Button):
        
    def left_click(self, mouse):
        self.parent.sorted_by = self.text
        
        
class Filename_Button(pride.gui.gui.Button):
    
    flags = {"selected" : False}
    
    def left_click(self, mouse):
        if not self.selected:
            self.selected = True
        else:
            self.allow_text_edit = True
            
            
class File_Open_Prompt(pride.gui.gui.Container):
                
    defaults = {"h_range" : (0, 200), "pack_mode" : "bottom",
                'a' : 255}
    
    def __init__(self, **kwargs):
        super(File_Open_Prompt, self).__init__(**kwargs)
        textbox = self.create("pride.gui.widgetlibrary.Text_Box", 
                              pack_mode="top", scroll_bars_enabled=False)
        self.create(Filetype_Filter_Selector)
        
        
class Filetype_Filter_Selector(pride.gui.widgetlibrary.Popup_Button):
    
    defaults = {"popup_type" : "pride.gui.pyobjecttest.List"}
    