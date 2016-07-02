# header crafter program
# palette with one button for adding to the header
# can select and edit header fields
# make size relative to header field

class Header_Crafter(pride.gui.gui.Application):
    
    def __init__(self, **kwargs):
        super(Header_Crafter, self).__init__(**kwargs)
        self.palette = application_window.create("pride.gui.widgetlibrary.Palette", 
                                                 button_types=("pride.gui.headercrafter.Field_Button", ),
                                                 pack_mode="left")
        self.work_area = application_window.create("pride.gui.headercrafter.Work_Space", pack_mode="main")
        
                                   
class Work_Space(pride.gui.gui.Window):
                                    
    def left_click(self, mouse):
        current_button = pride.objects[self.target_object].current_button
        if current_button is not None:
            self.create(current_button, position=(mouse.x, mouse.y))

    
class Field_Button(pride.gui.gui.Button): pass
    
    