import pride.gui.gui
import pride.utilities

class Service_Window(pride.gui.gui.Window):
    
    defaults = {"hidden" : True}
    

class Client_Window(pride.gui.gui.Window):
       
    def left_click(self, mouse):
        pride.objects[self.client].handle_mouse(pride.utilities.save_data(mouse.x, mouse.y, mouse.clicks, mouse.button))
        
    def right_click(self, mouse):
        pride.objects[self.client].handle_mouse(pride.utilities.save_data(mouse.x, mouse.y, mouse.clicks, mouse.button))