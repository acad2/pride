import mpre.gui.gui

class File_Explorer(mpre.gui.gui.Application):
    
    def __init__(self, **kwargs):
        super(File_Explorer, self).__init__(**kwargs)
        self.create(Navigation_Bar)
        self.create(Info_Bar, pack_mode="bottom")
      #  self.create(Directory_Viewer)        
        

class Navigation_Bar(mpre.gui.gui.Container):
            
    defaults = {"pack_mode" : "menu_bar"}
    
    def __init__(self, **kwargs):
        super(Navigation_Bar, self).__init__(**kwargs)
        #self.create(Back_Button)
        #self.create(Forward_Button)
        #self.create(History_Dropdown)
        #self.create(Ascend_Button)
        #self.create(Search_Bar)
        
        
class Places_Bar(mpre.gui.gui.Container):
            
    defaults = {"pack_mode" : "left"}
    
    def __init__(self, **kwargs):
        super(Places_Bar, self).__init__(**kwargs)
        #self.create(Lru_Directory_Dropdown)
        #self.create(Remote_Host_Dropdown)
        

class Info_Bar(mpre.gui.gui.Container):
            
    defaults = {"pack_mode" : "bottom"}
    
    def __init__(self, **kwargs):
        super(Info_Bar, self).__init__(**kwargs)
        #self.create(Item_Count_Indicator
        #self.create(Selection_Count_Indicator)
        #self.create(File_Size_Indicator)
        
        
class Directory_Viewer(mpre.gui.gui.Window):
        
    def __init__(self, **kwargs):
        super(Directory_Viewer, self).__init__(**kwargs)
        self.create(Places_Bar)
        self.create(Column_Viewer)
        #for attribute in self.display_attributes:
        #    container = self.create("mpre.gui.gui.Container", 
        #                            pack_mode="vertical")
        #    container.create(Sort_Button, text=attribute, pack_mode="top")
        #    container.create(Indicator, 
        #    self.create(Sort_Button, text=attribute)
        #    self.create(Directory_Listing
    
    
class Column_Viewer(mpre.gui.gui.Window):
        
    defaults = {"default_columns" : ("Type", "Name", "Size", 
                                     "Date_Created", "Date_Modified"),
                "pack_mode" : "vertical"}
                
    def __init__(self, **kwargs):
        super(Column_Viewer, self).__init__(**kwargs)
        for column_name in self.default_columns:
            container = self.create("mpre.gui.gui.Container")
          #  container.create(Sort_Button, value=column_name)
           # for 